"""Offline pinning and unperformed qualification checks, with synthetic versions."""

import copy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.create_workspace import REPOSITORY_ROOT, WorkspaceError
from scripts.runtime_lock import build_lock, check_lock, main, validate_schema


class RuntimeLockTests(unittest.TestCase):
    def arguments(self):
        # A synthetic expected version tests pinning; no installed release claim.
        return dict(provider="albert", model="qwen3-coder-30b-a3b-instruct", prompt_id="01_bugfix", run_id="synthetic-001", campaign_id="infrastructure-test", opencode_version="1.2.3")

    def test_complete_lock_has_exact_cell_hashes_and_explicit_unknowns(self):
        lock = build_lock(**self.arguments())
        check_lock(lock)
        self.assertEqual(lock["provider"], "albert")
        self.assertEqual(lock["protocol_track"], "restricted")
        self.assertEqual(lock["catalog_snapshot_sha256"], "0fc3ed2b2fc5c581a1d175cd6a98cb9b64c85bb850431eb1990650f5c5ab1e0e")
        self.assertIsNone(lock["observed_opencode_version"])
        self.assertIsNone(lock["opencode_artifact_sha256"])
        self.assertIsNone(lock["sandbox_review_id"])
        self.assertIsNotNone(lock["pytest_version"])
        self.assertTrue(lock["preparation_environment_only"])

    def test_lock_drift_and_scoring_without_qualification_are_rejected(self):
        lock = build_lock(**self.arguments())
        for field, value in (("prompt_sha256", "0" * 64), ("model_id", "openweight-code"), ("provider_config_sha256", "0" * 64), ("python_version", "0.0.0"), ("protocol_track", "agentic")):
            changed = copy.deepcopy(lock)
            changed[field] = value
            with self.subTest(field=field), self.assertRaises(WorkspaceError):
                check_lock(changed)
        with self.assertRaises(WorkspaceError):
            check_lock(lock, for_scoring=True)

    def test_floating_opencode_versions_and_unknown_models_are_rejected(self):
        for version in ("latest", "1", "1.2", ""):
            arguments = self.arguments()
            arguments["opencode_version"] = version
            with self.subTest(version=version), self.assertRaises(WorkspaceError):
                build_lock(**arguments)
        arguments = self.arguments()
        arguments["model"] = "deepseek-v4-flash"
        with self.assertRaises(WorkspaceError):
            build_lock(**arguments)

    def test_unperformed_preflight_cannot_be_promoted_or_claim_a_pass(self):
        path = REPOSITORY_ROOT / "runtime/preflight.albert.example.json"
        record = json.loads(path.read_text())
        validate_schema(record, "preflight.schema.json")
        changed = copy.deepcopy(record)
        changed["scored_ready"] = True
        with self.assertRaises(WorkspaceError):
            validate_schema(changed, "preflight.schema.json")
        for name in record["checks"]:
            changed = copy.deepcopy(record)
            changed["checks"][name]["status"] = "passed"
            with self.subTest(check=name), self.assertRaises(WorkspaceError):
                validate_schema(changed, "preflight.schema.json")

    def test_cli_creates_only_a_lock_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            output = Path(root) / "runtime.json"
            arguments = ["create", "--output", str(output)]
            for name, value in self.arguments().items():
                arguments += ["--" + name.replace("_", "-"), value]
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(arguments), 0)
            first = output.read_bytes()
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["check", "--manifest", str(output)]), 0)
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(arguments)
            self.assertEqual(output.read_bytes(), first)
            self.assertEqual([path.name for path in Path(root).iterdir()], ["runtime.json"])
