"""Aristote owner evidence, raw field semantics and canonical workspace selection."""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.aristote_catalog import (
    FLOATING, OPTIONAL, PRIMARY, SNAPSHOT, candidate_status, canonical_candidate,
    parse_catalog, read_catalog,
)
from scripts.create_workspace import REPOSITORY_ROOT, WorkspaceError, create_workspace
from scripts.runtime_lock import build_lock, check_lock, validate_schema


SNAPSHOT_SHA256 = "ace8258a30778b5a7eaef0ce22e20bbe2c95c15ba1c4c9b495b7589586312e69"


class AristoteCatalogTests(unittest.TestCase):
    def setUp(self):
        self.models, self.sha = read_catalog()
        self.metadata = json.loads((SNAPSHOT.parent.parent / "metadata.json").read_text())

    def test_exact_snapshot_hash_ids_and_owner_account_provenance(self):
        self.assertEqual(self.sha, SNAPSHOT_SHA256)
        self.assertEqual(self.metadata["catalog"]["sha256"], self.sha)
        self.assertEqual(self.metadata["catalog"]["source_endpoint"], "https://llm.aristote.education/v1/models")
        self.assertEqual(self.metadata["catalog"]["retrieval_date"], "2026-10-08")
        self.assertEqual(self.metadata["catalog"]["retrieved_by"], "repository_owner")
        self.assertEqual(set(self.models), set(PRIMARY) | set(OPTIONAL) | {FLOATING, "bge-m3", "bge-reranker-v2-m3"})

    def test_raw_fields_preserved_and_unsupported_semantics_remain_unknown(self):
        entries = self.metadata["models"] + self.metadata["excluded_models"] + self.metadata["floating_models"]
        self.assertEqual({entry["model_id"] for entry in entries}, set(self.models))
        for entry in entries:
            raw = self.models[entry["model_id"]]
            self.assertEqual(entry["api_record_raw"], raw)
            self.assertEqual(entry["api_owned_by_raw"], raw.get("owned_by"))
            self.assertEqual(entry["api_created_raw"], raw.get("created"))
            self.assertEqual(entry["api_mode_raw"], raw.get("mode"))
            self.assertEqual(entry["aliases"], raw.get("aliases"))
            self.assertFalse(entry["created_semantics_verified"])
            for field in ("upstream_model_ownership", "declared_max_context_length", "service_output_limit", "exact_served_checkpoint", "checkpoint_revision", "weight_revision", "served_quantization", "tokenizer", "decoding_implementation", "tool_call_verified", "latency", "throughput", "actual_pricing", "upstream_release_date"):
                self.assertIsNone(entry[field], (entry["model_id"], field))
        self.assertNotIn("mode", self.models["mistral-small-3.2-24b"])
        self.assertEqual(self.metadata["local_budget"]["basis"], "benchmark_extension_provisional_common_cap")
        self.assertIsNone(self.metadata["local_budget"]["service_context_limit"])
        self.assertIsNone(self.metadata["local_budget"]["service_output_limit"])

    def test_candidate_classification_distinguishes_modes_floating_and_optional(self):
        self.assertEqual(self.metadata["initial_model_order"], list(PRIMARY))
        self.assertEqual(self.metadata["default_model_id"], PRIMARY[0])
        for model_id in PRIMARY:
            self.assertEqual(candidate_status(self.models[model_id]), ("priority", None))
        for model_id in OPTIONAL:
            self.assertEqual(candidate_status(self.models[model_id]), ("optional", None))
        for model_id, mode in (("bge-m3", "embedding"), ("bge-reranker-v2-m3", "rerank")):
            status, reason = candidate_status(self.models[model_id])
            self.assertEqual(status, "excluded")
            self.assertIn(mode, reason)
            with self.assertRaises(WorkspaceError):
                canonical_candidate(self.models, model_id)
        self.assertEqual(candidate_status(self.models[FLOATING])[0], "floating_alias")
        with self.assertRaises(WorkspaceError):
            canonical_candidate(self.models, FLOATING)
        self.assertEqual(candidate_status({"id": "new-model"})[0], "unreviewed")
        self.assertEqual(candidate_status({"id": PRIMARY[0], "mode": "embedding"})[0], "excluded")
        self.assertEqual(candidate_status({"id": PRIMARY[0], "mode": "other-service"})[0], "unreviewed")

    def test_optional_fields_are_not_required_or_synthesized(self):
        raw = {"data": [{"id": PRIMARY[0]}]}
        models = parse_catalog(json.dumps(raw).encode())
        self.assertEqual(models[PRIMARY[0]], raw["data"][0])
        self.assertNotIn("mode", models[PRIMARY[0]])
        self.assertNotIn("aliases", models[PRIMARY[0]])
        self.assertIs(canonical_candidate(models, PRIMARY[0]), models[PRIMARY[0]])

    def test_strict_json_and_duplicate_or_invalid_records_fail_closed(self):
        malformed = [b'{}', b'{"data":{}}', b'{"data":[null]}', b'{"data":[[]]}', b'{"data":[{}]}', b'{"data":[{"id":1}]}', b'{"data":[{"id":" x "}]}', b'{"data":[],"data":[]}', b'{"data":[],"extra":NaN}', b'{"data":[]} trailing', b'\xff', b'{"data":[{"id":"x","id":"y"}]}']
        original = json.loads(SNAPSHOT.read_bytes())
        for mutate in (
            lambda rows: rows.append(copy.deepcopy(rows[0])),
            lambda rows: rows[0].update(mode=False),
            lambda rows: rows[0].update(object="other"),
        ):
            changed = copy.deepcopy(original)
            mutate(changed["data"])
            malformed.append(json.dumps(changed).encode())
        for data in malformed:
            with self.subTest(data=data), self.assertRaises(WorkspaceError):
                parse_catalog(data)

    def test_each_priority_model_selects_one_secret_free_workspace_config(self):
        configs = self.metadata["configs"]
        self.assertEqual({item["model_id"] for item in configs.values()}, set(PRIMARY))
        self.assertEqual(len(configs), len(PRIMARY))
        self.assertFalse((SNAPSHOT.parent.parent / "opencode.json").exists())
        with tempfile.TemporaryDirectory() as root:
            for number, model in enumerate(PRIMARY):
                workspace, metadata_path = create_workspace(benchmark="toy", provider="aristote", model=model, run_id=str(number), output_root=Path(root))
                config_path = SNAPSHOT.parent.parent / model / "opencode.json"
                self.assertEqual((workspace / "opencode.json").read_bytes(), config_path.read_bytes())
                config = json.loads((workspace / "opencode.json").read_bytes())
                self.assertEqual(config["model"], "aristote/" + model)
                self.assertEqual(set(config["provider"]["aristote"]["models"]), {model})
                self.assertNotIn("apiKey", config["provider"]["aristote"]["options"])
                self.assertEqual(json.loads(metadata_path.read_text())["catalog_snapshot_sha256"], self.sha)
                self.assertEqual({path.name for path in workspace.iterdir()}, {"toolbox.py", "test_toolbox.py", "opencode.json", ".git"})

    def test_unknown_alias_like_and_floating_ids_cannot_be_overridden_by_config(self):
        with tempfile.TemporaryDirectory() as root:
            for model in ("qwen3.6-35b", "Qwen-3.6-35b-instruct", "unknown", FLOATING, "bge-m3", "bge-reranker-v2-m3"):
                with self.subTest(model=model), self.assertRaises(WorkspaceError):
                    create_workspace(benchmark="toy", provider="aristote", model=model, run_id="invalid", output_root=Path(root), config_path=SNAPSHOT.parent.parent / PRIMARY[0] / "opencode.json")
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_catalog_hash_drift_fails_before_workspace_creation(self):
        with tempfile.TemporaryDirectory() as root:
            with patch("scripts.aristote_catalog.read_catalog", return_value=(self.models, "0" * 64)):
                with self.assertRaisesRegex(WorkspaceError, "catalog hash"):
                    create_workspace(benchmark="toy", provider="aristote", model=PRIMARY[0], run_id="drift", output_root=Path(root))
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_family_comparison_does_not_assert_checkpoint_equivalence(self):
        comparison = self.metadata["model_family_comparisons"][0]
        self.assertEqual(comparison["status"], "model-family-only")
        self.assertEqual(comparison["local_model_id"], "mistral-small-3.2-24b")
        self.assertEqual(comparison["model_id"], "mistral-small-3-2-24b-instruct-2506")
        self.assertIsNone(comparison["exact_checkpoint_identity"])

    def test_runtime_lock_and_preflight_template_preserve_unqualified_status(self):
        lock = build_lock(provider="aristote", model=PRIMARY[0], prompt_id="01_bugfix", run_id="synthetic", campaign_id="infrastructure-test", opencode_version="1.2.3")
        self.assertEqual(lock["catalog_snapshot_sha256"], self.sha)
        self.assertEqual(lock["provider_config_path"], "providers/aristote/" + PRIMARY[0] + "/opencode.json")
        check_lock(lock)
        record = json.loads((REPOSITORY_ROOT / "runtime/preflight.aristote.example.json").read_text())
        validate_schema(record, "preflight.schema.json")
        self.assertEqual(record["provider"], record["authentication"]["provider_id"])
        self.assertEqual(record["model_id"], PRIMARY[0])
        self.assertEqual(record["protocol_track"], "restricted")
        self.assertFalse(record["scored_ready"])
        for check in record["checks"].values():
            self.assertEqual(check["status"], "not_run")
            self.assertIsNone(check["observed_at"])
            self.assertIsNone(check["evidence_sha256"])
        self.assertIsNone(record["authentication"]["credential_storage_location"])
        self.assertFalse(record["authentication"]["credential_storage_location_verified"])

    def test_direct_cli_selects_canonical_id_and_rejects_renaming_without_traceback(self):
        with tempfile.TemporaryDirectory() as root:
            command = [sys.executable, str(REPOSITORY_ROOT / "scripts/create_workspace.py"), "--benchmark", "toy", "--provider", "aristote", "--run-id", "cli", "--output-root", root]
            environment = {"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1"}
            result = subprocess.run(command + ["--model", PRIMARY[0]], cwd=root, capture_output=True, text=True, env=environment, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            workspace = Path(json.loads(result.stdout)["workspace"])
            self.assertEqual(json.loads((workspace / "opencode.json").read_bytes())["model"], "aristote/" + PRIMARY[0])
            result = subprocess.run(command + ["--model", "qwen3.6-35b"], cwd=root, capture_output=True, text=True, env=environment, timeout=30)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)
