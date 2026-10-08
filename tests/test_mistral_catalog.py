"""Owner Mistral catalog, preferred IDs, apparent cards and offline integration."""

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

from scripts.create_workspace import REPOSITORY_ROOT, WorkspaceError, create_workspace
from scripts.mistral_catalog import (
    OPTIONAL, PRIMARY, SNAPSHOT, alias_clusters, candidate_status,
    canonical_candidate, parse_catalog, read_catalog,
)
from scripts.runtime_lock import build_lock, check_lock, validate_schema


SNAPSHOT_SHA256 = "4246145d5629c7106aaefe4e0831cd4d9e9178e868f3c3b9c5feaced36178373"


class MistralCatalogTests(unittest.TestCase):
    def setUp(self):
        self.models, self.sha = read_catalog()
        self.directory = SNAPSHOT.parent.parent
        self.metadata = json.loads((self.directory / "metadata.json").read_bytes())

    def test_snapshot_count_hash_owner_provenance_and_retirement(self):
        self.assertEqual(len(self.models), 46)
        self.assertEqual(self.sha, SNAPSHOT_SHA256)
        self.assertEqual(self.metadata["catalog"]["sha256"], self.sha)
        self.assertEqual(self.metadata["catalog"]["source_endpoint"], "https://api.mistral.ai/v1/models")
        self.assertEqual(self.metadata["catalog"]["retrieved_by"], "repository_owner")
        self.assertEqual(self.metadata["catalog"]["retrieval_date"], "2026-10-08")
        self.assertNotIn("zai-glm-5-3", self.models)
        self.assertEqual(self.metadata["retired_candidates"][0]["model_id"], "zai-glm-5-3")
        for filename in ("opencode.json", "opencode.medium.json"):
            self.assertFalse((self.directory / filename).exists())
        migration = self.metadata["migrated_configs"][0]
        self.assertEqual(migration["sha256_before"], migration["sha256_after"])
        self.assertEqual(hashlib.sha256((self.directory / migration["new_path"]).read_bytes()).hexdigest(), migration["sha256_before"])

    def test_raw_fields_aliases_capabilities_and_unknown_semantics_preserved(self):
        self.assertEqual({entry["model_id"] for entry in self.metadata["models"]}, set(self.models))
        for entry in self.metadata["models"]:
            raw = self.models[entry["model_id"]]
            self.assertEqual(entry["api_record_raw"], raw)
            self.assertEqual(entry["aliases"], raw["aliases"])
            self.assertEqual(entry["capabilities_advertised"], raw["capabilities"])
            self.assertEqual(entry["declared_max_context_length"], raw["max_context_length"])
            self.assertEqual(entry["api_created_raw"], raw["created"])
            self.assertFalse(entry["created_semantics_verified"])
            for field in ("upstream_model_ownership", "exact_served_checkpoint", "checkpoint_revision", "served_quantization", "tokenizer", "decoding_implementation", "service_output_limit", "tool_call_verified", "latency", "throughput", "actual_pricing", "upstream_release_timestamp"):
                self.assertIsNone(entry[field])

    def test_alias_ids_are_valid_records_and_clusters_do_not_attest_weights(self):
        clusters = alias_clusters(self.models)
        self.assertEqual(clusters, self.metadata["alias_clusters"])
        self.assertEqual(len(clusters), 17)
        self.assertEqual(sum(len(cluster["catalog_ids"]) for cluster in clusters), 46)
        self.assertIn("mistral-medium-latest", self.models["mistral-medium-3-5"]["aliases"])
        for cluster in clusters:
            self.assertIsNone(cluster["exact_served_checkpoint_identity"])
            self.assertFalse(cluster["served_checkpoint_equivalence_verified"])
        medium = next(cluster for cluster in clusters if cluster["preferred_benchmark_id"] == PRIMARY[0])
        self.assertEqual(len(medium["catalog_ids"]), 9)
        # Equal billing names do not merge the two distinct OCR 4 cards.
        ocr = [cluster for cluster in clusters if cluster["apparent_shared_model_card"]["billing_model_name"] == "mistral-ocr-4"]
        self.assertEqual(len(ocr), 2)

    def test_alias_reciprocity_and_card_consistency_fail_closed(self):
        for mutate in (
            lambda rows: rows[1].update(aliases=[]),
            lambda rows: rows[1].update(billing_model_name="different-card"),
            lambda rows: rows[1]["capabilities"].update(function_calling=False),
            lambda rows: rows[1].update(max_context_length=123),
        ):
            catalog = json.loads(SNAPSHOT.read_bytes())
            mutate(catalog["data"])
            with self.subTest(mutate=mutate), self.assertRaises(WorkspaceError):
                parse_catalog(json.dumps(catalog).encode())
        raw = copy.deepcopy(self.models[PRIMARY[0]])
        raw["aliases"] = ["external-alias-not-returned"]
        models = parse_catalog(json.dumps({"object": "list", "data": [raw]}).encode())
        self.assertEqual(set(models), {PRIMARY[0]})
        self.assertEqual(alias_clusters(models)[0]["external_aliases_not_returned"], raw["aliases"])

    def test_only_preferred_stable_ids_are_candidates_and_capabilities_control_exclusions(self):
        self.assertEqual(self.metadata["initial_model_order"], list(PRIMARY))
        self.assertEqual(self.metadata["optional_model_ids"], list(OPTIONAL))
        for model_id, entry in self.models.items():
            if model_id in PRIMARY + OPTIONAL:
                self.assertIs(canonical_candidate(self.models, model_id), entry)
            else:
                with self.subTest(model_id=model_id), self.assertRaises(WorkspaceError):
                    canonical_candidate(self.models, model_id)
        for model_id in self.metadata["excluded_model_ids"]:
            entry = self.models[model_id]
            self.assertIs(entry["capabilities"]["completion_chat"], False)
            self.assertIn("completion_chat=false", candidate_status(entry)[1])
        self.assertEqual(len(self.metadata["excluded_model_ids"]), 19)
        self.assertEqual(len(self.metadata["non_initial_audio_chat_ids"]), 2)
        entry = copy.deepcopy(self.models[PRIMARY[0]])
        entry["capabilities"]["completion_chat"] = False
        self.assertEqual(candidate_status(entry)[0], "excluded")
        entry["capabilities"] = {}
        self.assertEqual(candidate_status(entry)[0], "unreviewed")
        self.assertIn("Lean/formal-proof", candidate_status(self.models["labs-leanstral-1-5-1"])[1])

    def test_invalid_utf8_json_ids_capabilities_and_duplicates_are_rejected(self):
        malformed = [b'\xff', b'{"object":"list","data":[],"data":[]}', b'{"object":"list","data":[],"extra":NaN}', b'{}', b'{"object":"list","data":[null]}', b'{"object":"list","data":{}}']
        for mutate in (
            lambda rows: rows.append(copy.deepcopy(rows[0])),
            lambda rows: rows[0].update(id="has spaces"),
            lambda rows: rows[0].update(id=""),
            lambda rows: rows[0].update(id=True),
            lambda rows: rows[0].update(capabilities=[]),
            lambda rows: rows[0]["capabilities"].update(function_calling=1),
            lambda rows: rows[0].update(aliases=["duplicate", "duplicate"]),
            lambda rows: rows[0].update(aliases=None),
            lambda rows: rows[0].update(max_context_length=False),
        ):
            catalog = json.loads(SNAPSHOT.read_bytes())
            mutate(catalog["data"])
            malformed.append(json.dumps(catalog).encode())
        for data in malformed:
            with self.subTest(data=data[:80]), self.assertRaises(WorkspaceError):
                parse_catalog(data)

    def test_three_configs_select_preferred_models_without_leaking_evaluator_material(self):
        self.assertEqual({item["model_id"] for item in self.metadata["configs"].values()}, set(PRIMARY))
        with tempfile.TemporaryDirectory() as root:
            for number, model in enumerate(PRIMARY):
                workspace, metadata_path = create_workspace(benchmark="toy", provider="mistral", model=model, run_id=str(number), output_root=Path(root))
                self.assertEqual((workspace / "opencode.json").read_bytes(), (self.directory / model / "opencode.json").read_bytes())
                self.assertEqual(json.loads(metadata_path.read_text())["catalog_snapshot_sha256"], self.sha)
                self.assertEqual({path.name for path in workspace.iterdir()}, {"toolbox.py", "test_toolbox.py", "opencode.json", ".git"})
            for model in ("zai-glm-5-3", "mistral-medium-latest", "codestral-latest", "mistral-small-latest", "mistral-medium-2604", "unknown", "mistral-embed"):
                with self.subTest(model=model), self.assertRaises(WorkspaceError):
                    create_workspace(benchmark="toy", provider="mistral", model=model, run_id="invalid", output_root=Path(root), config_path=self.directory / PRIMARY[0] / "opencode.json")

    def test_catalog_hash_drift_and_missing_preferred_id_are_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            with patch("scripts.mistral_catalog.read_catalog", return_value=(self.models, "0" * 64)):
                with self.assertRaisesRegex(WorkspaceError, "catalog hash"):
                    create_workspace(benchmark="toy", provider="mistral", model=PRIMARY[0], run_id="drift", output_root=Path(root))
            self.assertEqual(list(Path(root).iterdir()), [])
            path = Path(root) / "catalog.json"
            path.write_text('{"object":"list","data":[]}')
            with self.assertRaises(WorkspaceError):
                read_catalog(path)

    def test_evidence_conflict_caps_and_family_only_comparison_remain_explicit(self):
        evidence = self.metadata["public_evidence"]
        data = (self.directory / evidence["path"]).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), evidence["sha256"])
        public = json.loads(data)
        conflict = public["evidence_conflicts"][0]
        self.assertEqual(conflict, self.metadata["evidence_conflicts"][0])
        self.assertEqual(conflict["owner_catalog_value"], 256000)
        self.assertEqual(conflict["public_documentation_value_raw"], "128k")
        self.assertEqual(conflict["status"], "unresolved")
        self.assertIsNone(conflict["resolution"])
        self.assertIsNone(conflict["public_documentation_exact_tokens"])
        self.assertEqual(self.metadata["local_budget"]["basis"], "benchmark_extension_provisional_common_cap")
        self.assertEqual(self.metadata["model_family_comparisons"][0]["status"], "model-family-only")
        self.assertIsNone(self.metadata["model_family_comparisons"][0]["exact_checkpoint_identity"])

    def test_runtime_lock_and_unperformed_mistral_template(self):
        lock = build_lock(provider="mistral", model=PRIMARY[0], prompt_id="01_bugfix", run_id="synthetic", campaign_id="infrastructure-test", opencode_version="1.2.3")
        self.assertEqual(lock["catalog_snapshot_sha256"], self.sha)
        check_lock(lock)
        record = json.loads((REPOSITORY_ROOT / "runtime/preflight.mistral.example.json").read_bytes())
        validate_schema(record, "preflight.schema.json")
        self.assertEqual(record["provider"], "mistral")
        self.assertEqual(record["model_id"], "codestral-2508")
        self.assertEqual(record["protocol_track"], "restricted")
        self.assertFalse(record["scored_ready"])
        for check in record["checks"].values():
            self.assertEqual(check["status"], "not_run")
            self.assertIsNone(check["observed_at"])
            self.assertIsNone(check["evidence_sha256"])

    def test_direct_cli_selects_primary_and_rejects_floating_id_without_traceback(self):
        with tempfile.TemporaryDirectory() as root:
            command = [sys.executable, str(REPOSITORY_ROOT / "scripts/create_workspace.py"), "--benchmark", "toy", "--provider", "mistral", "--run-id", "cli", "--output-root", root]
            environment = {"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1"}
            result = subprocess.run(command + ["--model", PRIMARY[0]], cwd=root, capture_output=True, text=True, env=environment, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads((Path(json.loads(result.stdout)["workspace"]) / "opencode.json").read_bytes())["model"], "mistral/" + PRIMARY[0])
            result = subprocess.run(command + ["--model", "mistral-medium-latest"], cwd=root, capture_output=True, text=True, env=environment, timeout=30)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)
