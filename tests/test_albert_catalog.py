"""Owner catalog evidence, canonical-ID policy and workspace selection."""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.albert_catalog import (
    EXCLUDED, OPTIONAL, PRIMARY, SNAPSHOT, candidate_status, canonical_candidate,
    parse_catalog, read_catalog,
)
from scripts.create_workspace import REPOSITORY_ROOT, WorkspaceError, create_workspace


class AlbertCatalogTests(unittest.TestCase):
    def setUp(self):
        self.models, self.sha = read_catalog()
        self.metadata = json.loads((SNAPSHOT.parent.parent / "metadata.json").read_text())

    def test_exact_snapshot_hash_and_owner_provenance(self):
        self.assertEqual(self.sha, "0fc3ed2b2fc5c581a1d175cd6a98cb9b64c85bb850431eb1990650f5c5ab1e0e")
        self.assertEqual(self.metadata["catalog"]["sha256"], self.sha)
        self.assertEqual(self.metadata["catalog"]["retrieval_date"], "2026-10-08")
        self.assertEqual(self.metadata["catalog"]["retrieved_by"], "repository_owner")
        self.assertEqual(len(self.models), 11)

    def test_metadata_preserves_every_catalog_declaration_and_unknown(self):
        entries = self.metadata["models"] + self.metadata["excluded_models"]
        self.assertEqual({entry["model_id"] for entry in entries}, set(self.models))
        for entry in entries:
            raw = self.models[entry["model_id"]]
            for field, source in (("aliases", "aliases"), ("model_type", "type"), ("owned_by", "owned_by"), ("declared_max_context_length", "max_context_length")):
                self.assertEqual(entry[field], raw[source])
            self.assertEqual(entry["advertised_prompt_token_cost"], raw["costs"]["prompt_tokens"])
            self.assertEqual(entry["advertised_completion_token_cost"], raw["costs"]["completion_tokens"])
            for field in ("checkpoint_revision", "served_quantization", "decoding_implementation", "service_output_limit", "tool_call_verified", "agentic_quality", "latency", "throughput"):
                self.assertIsNone(entry[field])

    def test_priority_optional_and_unsuitable_types_are_separate(self):
        self.assertEqual(self.metadata["default_model_id"], PRIMARY[0])
        self.assertEqual(self.metadata["initial_model_order"], list(PRIMARY))
        for model_id in PRIMARY:
            self.assertEqual(candidate_status(self.models[model_id]), ("priority", None))
        for model_id in OPTIONAL:
            self.assertEqual(candidate_status(self.models[model_id]), ("optional", None))
        for model_id in EXCLUDED:
            self.assertEqual(candidate_status(self.models[model_id])[0], "excluded")
            with self.assertRaises(WorkspaceError):
                canonical_candidate(self.models, model_id)
        self.assertEqual(candidate_status(self.models["lightonocr-2-1b"])[0], "excluded")

    def test_owner_basic_observation_does_not_complete_formal_qualification(self):
        qualification = self.metadata["qualification"]
        observation = qualification["owner_observation"]
        self.assertEqual(observation["model_id"], PRIMARY[0])
        self.assertEqual(observation["protocol_track"], "restricted")
        self.assertEqual(observation["basic_inference"], "owner_reported_success")
        self.assertEqual(observation["file_editing"], "owner_reported_success")
        self.assertIsNone(observation["observed_at"])
        self.assertIsNone(observation["evidence_sha256"])
        self.assertFalse(observation["formal_preflight_complete"])
        self.assertFalse(qualification["scored_ready"])
        self.assertIsNone(qualification["preflight_record"])

    def test_aliases_and_obsolete_id_never_resolve_as_canonical_candidates(self):
        for model_id in ["Mistral-Medium-3.5-128B"] + [alias for model in self.models.values() for alias in model["aliases"]]:
            with self.subTest(model_id=model_id), self.assertRaises(WorkspaceError):
                canonical_candidate(self.models, model_id)
        self.assertFalse((SNAPSHOT.parent.parent / "opencode.json").exists())
        self.assertEqual({item["model_id"] for item in self.metadata["configs"].values()}, set(PRIMARY))

    def test_default_workspace_selection_uses_exact_model_and_records_catalog_hash(self):
        with tempfile.TemporaryDirectory() as root:
            for number, model_id in enumerate(PRIMARY):
                workspace, path = create_workspace(benchmark="toy", provider="albert", model=model_id, run_id=str(number), output_root=Path(root))
                self.assertEqual(json.loads((workspace / "opencode.json").read_text())["model"], "albert/" + model_id)
                self.assertEqual(json.loads(path.read_text())["catalog_snapshot_sha256"], self.sha)
                self.assertFalse((workspace / "AGENTS.md").exists())
            with self.assertRaises(WorkspaceError):
                create_workspace(benchmark="toy", provider="albert", model="openweight-code", run_id="alias", output_root=Path(root))

    def test_malformed_catalogs_fail_closed(self):
        original = json.loads(SNAPSHOT.read_bytes())
        malformed = [{}, {"object": "list", "data": {}}, {"object": "list", "data": [None]}]
        for mutate in (
            lambda rows: rows.append(copy.deepcopy(rows[0])),
            lambda rows: rows[0].update(aliases=["same", "same"]),
            lambda rows: rows[0].update(max_context_length=True),
            lambda rows: rows[0].update(costs={"prompt_tokens": -1, "completion_tokens": 0}),
            lambda rows: rows[0].update(aliases=[rows[1]["id"]]),
        ):
            catalog = copy.deepcopy(original)
            mutate(catalog["data"])
            malformed.append(catalog)
        for catalog in malformed:
            with self.subTest(catalog=catalog), self.assertRaises(WorkspaceError):
                parse_catalog(json.dumps(catalog).encode())
        with self.assertRaises(WorkspaceError):
            parse_catalog(b'{"object":"list","object":"list","data":[]}')
        with self.assertRaises(WorkspaceError):
            parse_catalog(SNAPSHOT.read_bytes().replace(b'"prompt_tokens":0.0', b'"prompt_tokens":1e999', 1))

    def test_direct_cli_rejects_alias_without_traceback_or_partial_workspace(self):
        with tempfile.TemporaryDirectory() as root:
            result = subprocess.run([
                sys.executable, str(REPOSITORY_ROOT / "scripts/create_workspace.py"),
                "--benchmark", "toy", "--provider", "albert", "--model", "openweight-code",
                "--run-id", "alias-cli", "--output-root", root,
            ], cwd=root, capture_output=True, text=True,
                env={"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=30)
            self.assertEqual(result.returncode, 1)
            self.assertIn("canonical catalog ID", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(list(Path(root).iterdir()), [])
