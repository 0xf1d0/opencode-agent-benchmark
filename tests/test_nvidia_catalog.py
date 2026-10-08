"""Offline NVIDIA catalog, safe canonical mapping and unperformed qualification."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.nvidia_catalog import (
    COMPARISON, EXCLUDED, FIRST_PREFLIGHT, OPTIONAL, PRIMARY, PROFILE_DIRECTORIES,
    SNAPSHOT, candidate_status, canonical_candidate, parse_catalog, read_catalog, registered_profile,
)
from scripts.create_workspace import REPOSITORY_ROOT, WorkspaceError, create_workspace, git
from scripts.runtime_lock import build_lock, check_lock, validate_schema


SNAPSHOT_SHA256 = "2e7d19e2a7d4d8602a2b039de78b4af3e8b45920d34f50393947e53457d6849d"


class NvidiaCatalogTests(unittest.TestCase):
    def setUp(self):
        self.models, self.sha = read_catalog()
        self.directory = SNAPSHOT.parent.parent
        self.metadata = json.loads((self.directory / "metadata.json").read_bytes())

    def test_snapshot_exact_bytes_owner_http_provenance_and_record_count(self):
        self.assertEqual(self.sha, SNAPSHOT_SHA256)
        self.assertEqual(len(self.models), 80)
        catalog = self.metadata["catalog"]
        self.assertEqual(catalog["sha256"], self.sha)
        self.assertEqual(catalog["record_count"], 80)
        self.assertEqual(catalog["source_endpoint"], "https://integrate.api.nvidia.com/v1/models")
        self.assertEqual(catalog["retrieval_date"], "2026-10-08")
        self.assertEqual(catalog["retrieved_by"], "repository_owner")
        self.assertEqual(catalog["http_status"], 200)

    def test_raw_fields_preserved_no_aliases_or_invented_capabilities(self):
        entries = self.metadata["models"] + self.metadata["excluded_models"] + self.metadata["unreviewed_models"]
        self.assertEqual(len(entries), 80)
        self.assertEqual({entry["model_id"] for entry in entries}, set(self.models))
        for entry in entries:
            raw = self.models[entry["model_id"]]
            self.assertEqual(entry["api_record_raw"], raw)
            self.assertEqual(entry["api_owned_by_raw"], raw["owned_by"])
            self.assertEqual(entry["api_created_raw"], 735790403)
            self.assertFalse(entry["created_semantics_verified"])
            for field in ("aliases", "upstream_release_date", "upstream_model_ownership", "declared_max_context_length", "completion_chat", "function_calling", "reasoning", "tool_call_support", "service_output_limit", "exact_served_checkpoint", "checkpoint_revision", "weight_revision", "served_quantization", "tokenizer", "decoding_implementation", "modality", "pricing", "latency", "throughput", "tool_call_verified"):
                self.assertIsNone(entry[field], (entry["model_id"], field))
            self.assertEqual((entry["candidate_status"], entry["classification_reason"]), candidate_status(raw))

    def test_strict_utf8_json_shape_records_and_required_sparse_fields(self):
        original = json.loads(SNAPSHOT.read_bytes())
        malformed = [b'{}', b'{"object":"list","data":{}}', b'{"object":"other","data":[]}', b'{"object":"list","data":[null]}', b'{"object":"list","data":[],"data":[]}', b'{"object":"list","data":[],"x":NaN}', b'{"object":"list","data":[],"x":Infinity}', b'\xff', b'{} trailing']
        for update in ({"id": "../escape"}, {"id": "nvidia/../../escape"}, {"id": 1}, {"object": "list"}, {"created": True}, {"created": None}, {"owned_by": None}, {"owned_by": ""}):
            changed = copy.deepcopy(original)
            changed["data"][0].update(update)
            malformed.append(json.dumps(changed).encode())
        for key in ("id", "object", "created", "owned_by"):
            changed = copy.deepcopy(original)
            del changed["data"][0][key]
            malformed.append(json.dumps(changed).encode())
        changed = copy.deepcopy(original)
        changed["data"].append(copy.deepcopy(changed["data"][0]))
        malformed.append(json.dumps(changed).encode())
        for data in malformed:
            with self.subTest(data=data[:100]), self.assertRaises(WorkspaceError):
                parse_catalog(data)

    def test_no_optional_capability_fields_required_or_synthesized(self):
        raw = {"id": PRIMARY[0], "object": "model", "created": 735790403, "owned_by": "raw-label", "extra": {"preserved": True}}
        models = parse_catalog(json.dumps({"object": "list", "data": [raw]}).encode())
        self.assertEqual(models[PRIMARY[0]], raw)
        self.assertNotIn("aliases", models[PRIMARY[0]])
        self.assertNotIn("capabilities", models[PRIMARY[0]])

    def test_policy_keeps_optional_comparison_and_ambiguous_models_inactive(self):
        self.assertEqual(self.metadata["initial_model_order"], list(PRIMARY))
        self.assertEqual(self.metadata["default_model_id"], FIRST_PREFLIGHT)
        self.assertEqual(len(EXCLUDED), 18)
        self.assertEqual(len(self.metadata["unreviewed_models"]), 53)
        for model_id in PRIMARY:
            self.assertEqual(candidate_status(self.models[model_id]), ("priority", None))
        for model_id in OPTIONAL:
            self.assertEqual(candidate_status(self.models[model_id])[0], "optional")
        self.assertEqual(candidate_status(self.models[COMPARISON])[0], "comparison_candidate")
        self.assertEqual(candidate_status({"id": "nvidia/new-embed-looking-name", "owned_by": "nvidia"})[0], "unreviewed")
        for model_id in set(self.models) - set(PRIMARY):
            with self.subTest(model_id=model_id), self.assertRaises(WorkspaceError):
                canonical_candidate(self.models, model_id)

    def test_safe_mapping_is_explicit_unique_and_registry_tampering_fails(self):
        self.assertEqual(self.metadata["canonical_id_to_profile_directory"], PROFILE_DIRECTORIES)
        self.assertEqual(len(set(PROFILE_DIRECTORIES.values())), len(PRIMARY))
        for model_id, directory in PROFILE_DIRECTORIES.items():
            self.assertNotIn("/", directory)
            self.assertEqual(registered_profile(self.metadata, model_id), directory + "/opencode.json")
        for relative in ("../opencode.json", "/tmp/opencode.json", PRIMARY[0] + "/opencode.json"):
            changed = copy.deepcopy(self.metadata)
            entry = changed["configs"].pop(PROFILE_DIRECTORIES[PRIMARY[0]] + "/opencode.json")
            changed["configs"][relative] = entry
            with self.assertRaises(WorkspaceError):
                registered_profile(changed, PRIMARY[0])
        changed = copy.deepcopy(self.metadata)
        changed["canonical_id_to_profile_directory"][PRIMARY[0]] = "../escape"
        with self.assertRaises(WorkspaceError):
            registered_profile(changed, PRIMARY[0])
        changed = copy.deepcopy(self.metadata)
        changed["configs"]["duplicate/opencode.json"] = {"model_id": PRIMARY[0]}
        with self.assertRaises(WorkspaceError):
            registered_profile(changed, PRIMARY[0])

    def test_all_primary_slash_ids_prepare_only_agent_allowlist_and_clean_git(self):
        with tempfile.TemporaryDirectory() as root:
            for index, model_id in enumerate(PRIMARY):
                workspace, metadata_path = create_workspace(benchmark="toy", provider="nvidia", model=model_id, run_id=str(index), output_root=Path(root))
                source = self.directory / PROFILE_DIRECTORIES[model_id] / "opencode.json"
                self.assertEqual((workspace / "opencode.json").read_bytes(), source.read_bytes())
                config = json.loads(source.read_bytes())
                self.assertEqual(config["model"], "nvidia/" + model_id)
                self.assertEqual(set(config["provider"]["nvidia"]["models"]), {model_id})
                self.assertEqual({p.name for p in workspace.iterdir()}, {"toolbox.py", "test_toolbox.py", "opencode.json", ".git"})
                self.assertEqual(git(workspace, "status", "--porcelain"), "")
                self.assertEqual(git(workspace, "rev-list", "--count", "HEAD"), "1")
                initial = json.loads(metadata_path.read_bytes())
                self.assertEqual(initial["catalog_snapshot_sha256"], self.sha)
                self.assertEqual(initial["model_id"], model_id)
                self.assertNotIn(workspace, metadata_path.parents)
                with self.assertRaises(WorkspaceError):
                    create_workspace(benchmark="toy", provider="nvidia", model=model_id, run_id=str(index), output_root=Path(root))

    def test_unknown_nonselected_and_traversal_ids_fail_even_with_override(self):
        with tempfile.TemporaryDirectory() as root:
            for model_id in ("glm-5.3", "nvidia/nemotron-3.5-lightning", "NVIDIA/nemotron-3.5-lightning-30b-a3b", "nvidia/../../escape", *OPTIONAL, COMPARISON, *EXCLUDED):
                with self.subTest(model=model_id), self.assertRaises(WorkspaceError):
                    create_workspace(benchmark="toy", provider="nvidia", model=model_id, run_id="invalid", output_root=Path(root), config_path=self.directory / PROFILE_DIRECTORIES[PRIMARY[0]] / "opencode.json")
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_snapshot_and_configuration_drift_fail_closed(self):
        with tempfile.TemporaryDirectory() as root:
            with patch("scripts.nvidia_catalog.read_catalog", return_value=(self.models, "0" * 64)):
                with self.assertRaisesRegex(WorkspaceError, "catalog hash"):
                    create_workspace(benchmark="toy", provider="nvidia", model=PRIMARY[0], run_id="drift", output_root=Path(root))
            config = json.loads((self.directory / PROFILE_DIRECTORIES[PRIMARY[0]] / "opencode.json").read_bytes())
            config["provider"]["nvidia"]["models"][PRIMARY[0]]["name"] = "changed label"
            override = Path(root) / "modified.json"
            override.write_text(json.dumps(config))
            with self.assertRaisesRegex(WorkspaceError, "configuration hash"):
                create_workspace(benchmark="toy", provider="nvidia", model=PRIMARY[0], run_id="drift", output_root=Path(root), config_path=override)

    def test_public_evidence_separate_hashed_and_retirement_preserves_provenance(self):
        evidence = self.metadata["public_evidence"]
        path = self.directory / evidence["path"]
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), evidence["sha256"])
        facts = json.loads(path.read_bytes())
        self.assertTrue(facts["not_an_authenticated_catalog"])
        self.assertEqual({source["model_id"] for source in facts["sources"]}, set(PRIMARY))
        self.assertFalse((self.directory / "opencode.json").exists())
        retired = self.metadata["retired_configs"][0]
        self.assertEqual(retired["sha256"], "859dfc2485a0c475d966684b035e1d9669969cc51748177c1cc3533b01ff4149")
        self.assertEqual(hashlib.sha256((self.directory / retired["replacement"]).read_bytes()).hexdigest(), retired["sha256"])
        self.assertEqual(self.metadata["local_budget"]["basis"], "benchmark_extension_provisional_common_cap")
        for key in ("service_context_limit", "service_output_limit"):
            self.assertIsNone(self.metadata["local_budget"][key])

    def test_family_pairing_never_claims_identical_checkpoint(self):
        pair = self.metadata["model_family_comparisons"][0]
        self.assertEqual(pair["local_model_id"], COMPARISON)
        self.assertEqual(pair["status"], "model-family-only")
        self.assertIsNone(pair["exact_checkpoint_identity"])
        contrasts = self.metadata["non_equivalent_comparisons"]
        self.assertIn("different_model_sizes", contrasts[0]["status"])
        self.assertIn("different_version", contrasts[1]["status"])

    def test_runtime_lock_and_blank_lightning_preflight_do_not_promote_readiness(self):
        lock = build_lock(provider="nvidia", model=FIRST_PREFLIGHT, prompt_id="01_bugfix", run_id="synthetic", campaign_id="infrastructure-test", opencode_version="1.2.3")
        check_lock(lock)
        self.assertEqual(lock["catalog_snapshot_sha256"], self.sha)
        self.assertEqual(lock["provider_config_path"], "providers/nvidia/" + PROFILE_DIRECTORIES[FIRST_PREFLIGHT] + "/opencode.json")
        record = json.loads((REPOSITORY_ROOT / "runtime/preflight.nvidia.example.json").read_bytes())
        validate_schema(record, "preflight.schema.json")
        self.assertEqual(record["provider"], record["authentication"]["provider_id"])
        self.assertEqual(record["model_id"], FIRST_PREFLIGHT)
        self.assertEqual(record["protocol_track"], "restricted")
        for check in record["checks"].values():
            self.assertEqual(check["status"], "not_run")
            self.assertIsNone(check["observed_at"])
            self.assertIsNone(check["evidence_sha256"])
        self.assertFalse(record["scored_ready"])
        self.assertIsNone(record["authentication"]["credential_storage_location"])
        self.assertFalse(record["authentication"]["credential_storage_location_verified"])
        self.assertFalse(self.metadata["qualification"]["scored_ready"])
        with self.assertRaises(WorkspaceError):
            check_lock(lock, for_scoring=True)

    def test_direct_cli_slash_model_selection_and_fail_closed_without_traceback(self):
        with tempfile.TemporaryDirectory() as root:
            command = [sys.executable, str(REPOSITORY_ROOT / "scripts/create_workspace.py"), "--benchmark", "toy", "--provider", "nvidia", "--run-id", "cli", "--output-root", root]
            environment = {"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1"}
            result = subprocess.run(command + ["--model", FIRST_PREFLIGHT], cwd=root, capture_output=True, text=True, env=environment, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            for model_id in ("glm-5.3", "nvidia/../../escape", OPTIONAL[0]):
                result = subprocess.run(command + ["--model", model_id], cwd=root, capture_output=True, text=True, env=environment, timeout=30)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn("Traceback", result.stderr)
