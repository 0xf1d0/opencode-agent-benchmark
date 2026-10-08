"""Workspace isolation/credential regressions; no models or task solutions."""

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.create_workspace import (
    FIXTURE_FILES, REPOSITORY_ROOT, WorkspaceError, create_workspace, git,
)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repository = self.root / "repository"
        fixture = self.repository / "benchmark" / "toy" / "fixture"
        fixture.mkdir(parents=True)
        for filename in FIXTURE_FILES:
            shutil.copyfile(REPOSITORY_ROOT / "benchmark" / "toy" / "fixture" / filename, fixture / filename)
        shutil.copyfile(
            REPOSITORY_ROOT / "benchmark" / "toy" / "fixture_manifest.json",
            fixture.parent / "fixture_manifest.json",
        )
        (fixture / "auth.json").write_text('"fixture-secret-sentinel"')
        (fixture / ".env").write_text("API_KEY=dotenv-secret-sentinel")
        (fixture / "__pycache__").mkdir()
        (fixture.parent / "oracle").mkdir()
        (fixture.parent / "oracle" / "test_secret.py").write_text("oracle-sentinel")
        (self.repository / "AGENTS.md").write_text("benchmark-guide-sentinel")
        self.config_path = self.root / "selected.json"
        self.config = {
            "$schema": "https://opencode.ai/config.json",
            "model": "test-provider/test-model",
            "small_model": "test-provider/test-model",
            "autoupdate": False,
            "share": "disabled",
            "provider": {
                "test-provider": {
                    "npm": "@ai-sdk/openai-compatible",
                    "options": {
                        "baseURL": "https://inference.example.invalid/v1",
                        "apiKey": "{env:TEST_API_KEY}",
                    },
                    "models": {"test-model": {"limit": {"context": 32768, "output": 4096}}},
                },
            },
        }
        self.write_config()
        self.output_root = self.root / "output"
        self.arguments = dict(
            benchmark="toy", provider="test-provider", model="test-model", run_id="001",
            config_path=self.config_path, output_root=self.output_root,
            repository_root=self.repository,
        )

    def write_config(self, config=None):
        self.config_path.write_text(json.dumps(self.config if config is None else config, indent=2) + "\n")

    def test_exact_allowlist_and_independent_clean_baseline(self):
        (self.repository / "benchmark" / "toy" / "fixture" / "foreign-link").symlink_to(self.config_path)
        workspace, metadata_path = create_workspace(**self.arguments)
        self.assertEqual({path.name for path in workspace.iterdir()}, {*FIXTURE_FILES, "opencode.json", ".git"})
        self.assertNotIn(workspace, metadata_path.parents)
        for filename in FIXTURE_FILES:
            self.assertEqual((workspace / filename).read_bytes(),
                             (self.repository / "benchmark" / "toy" / "fixture" / filename).read_bytes())
        self.assertEqual((workspace / "opencode.json").read_bytes(), self.config_path.read_bytes())
        self.assertEqual(set(git(workspace, "ls-files").splitlines()), {*FIXTURE_FILES, "opencode.json"})
        self.assertEqual(git(workspace, "rev-list", "--count", "HEAD"), "1")
        self.assertEqual(git(workspace, "branch", "--show-current"), "main")
        self.assertEqual(git(workspace, "status", "--porcelain"), "")
        self.assertEqual(git(workspace, "remote"), "")
        self.assertEqual(git(workspace, "for-each-ref", "--format=%(refname)"), "refs/heads/main")
        metadata = json.loads(metadata_path.read_text())
        self.assertEqual(metadata["baseline_commit"], git(workspace, "rev-parse", "HEAD"))
        self.assertIsNone(metadata["model_family"])
        self.assertIsNone(metadata["opencode_version"])
        self.assertEqual(metadata["agents_md"], [])
        for filename, sha256 in metadata["files"].items():
            self.assertEqual(sha256, hashlib.sha256((workspace / filename).read_bytes()).hexdigest())
        (workspace / "toolbox.py").write_text("submission change")
        self.assertNotEqual((workspace / "toolbox.py").read_bytes(),
                            (self.repository / "benchmark" / "toy" / "fixture" / "toolbox.py").read_bytes())

    def test_environment_credentials_and_host_git_state_never_enter_workspace(self):
        foreign_git = self.root / "foreign.git"
        git(self.repository, "init", "--quiet", "--template=")
        template = self.root / "template"
        (template / "hooks").mkdir(parents=True)
        hook = template / "hooks" / "post-commit"
        hook.write_text("#!/bin/sh\ntouch " + str(self.root / "hook-ran") + "\n")
        hook.chmod(0o755)
        global_config = self.root / "global.gitconfig"
        global_config.write_text("[user]\n name = credential-sentinel\n email = credential-sentinel@invalid\n[commit]\n gpgSign = true\n")
        with patch.dict(os.environ, {
            "TEST_API_KEY": "environment-secret-sentinel", "GIT_DIR": str(foreign_git),
            "GIT_WORK_TREE": str(self.repository), "GIT_TEMPLATE_DIR": str(template),
            "GIT_CONFIG_GLOBAL": str(global_config), "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.hooksPath", "GIT_CONFIG_VALUE_0": str(template / "hooks"),
        }):
            workspace, _ = create_workspace(**self.arguments)
        self.assertFalse((self.root / "hook-ran").exists())
        self.assertFalse(foreign_git.exists())
        self.assertIn("{env:TEST_API_KEY}", (workspace / "opencode.json").read_text())
        for path in workspace.rglob("*"):
            if path.is_file():
                data = path.read_bytes()
                for sentinel in [b"environment-secret-sentinel", b"credential-sentinel", b"oracle-sentinel", b"benchmark-guide-sentinel", b"fixture-secret-sentinel", b"dotenv-secret-sentinel"]:
                    self.assertNotIn(sentinel, data, str(path))

    def test_existing_run_is_not_modified_even_for_another_model(self):
        workspace, metadata_path = create_workspace(**self.arguments)
        before = metadata_path.read_bytes()
        (workspace / "do-not-delete").write_text("preserve")
        self.config["model"] = "test-provider/other-model"
        self.config["small_model"] = self.config["model"]
        self.config["provider"]["test-provider"]["models"] = {"other-model": {}}
        self.write_config()
        with self.assertRaisesRegex(WorkspaceError, "refusing to overwrite"):
            create_workspace(**{**self.arguments, "model": "other-model"})
        self.assertEqual(metadata_path.read_bytes(), before)
        self.assertEqual((workspace / "do-not-delete").read_text(), "preserve")

    def test_existing_empty_run_is_not_reused(self):
        run = self.output_root / "toy" / "test-provider" / "001"
        run.mkdir(parents=True)
        with self.assertRaisesRegex(WorkspaceError, "refusing to overwrite"):
            create_workspace(**self.arguments)
        self.assertEqual(list(run.iterdir()), [])

    def test_literal_credentials_and_external_references_are_rejected_without_disclosure(self):
        cases = []
        for value in ["sk-secret-sentinel", "plain-secret-sentinel", "{file:/tmp/secret}", ""]:
            config = copy.deepcopy(self.config)
            config["provider"]["test-provider"]["options"]["apiKey"] = value
            cases.append(config)
        for value in ["Bearer plain-secret-sentinel", "plain-secret-sentinel"]:
            config = copy.deepcopy(self.config)
            config["provider"]["test-provider"]["options"]["headers"] = {"Authorization": value}
            cases.append(config)
        for url in ["https://user:plain-secret-sentinel@example.invalid/v1", "https://example.invalid/v1?api_key=plain-secret-sentinel"]:
            config = copy.deepcopy(self.config)
            config["provider"]["test-provider"]["options"]["baseURL"] = url
            cases.append(config)
        for config in cases:
            with self.subTest(config_case=len(json.dumps(config))):
                self.write_config(config)
                with self.assertRaises(WorkspaceError) as error:
                    create_workspace(**self.arguments)
                self.assertNotIn("secret-sentinel", str(error.exception))
                self.assertFalse(self.output_root.exists())

    def test_environment_authorization_is_preserved_without_expansion(self):
        self.config["provider"]["test-provider"]["options"]["headers"] = {
            "Authorization": "Bearer {env:TEST_API_KEY}", "Content-Type": "application/json",
        }
        self.write_config()
        workspace, _ = create_workspace(**self.arguments)
        self.assertEqual((workspace / "opencode.json").read_bytes(), self.config_path.read_bytes())

    def test_model_mismatch_auxiliary_routing_and_extra_provider_are_rejected(self):
        variants = [copy.deepcopy(self.config) for _ in range(3)]
        variants[0]["model"] = "test-provider/other-model"
        variants[1]["small_model"] = "foreign/other-model"
        variants[2]["provider"]["foreign"] = {}
        for config in variants:
            with self.subTest(config=config["model"]):
                self.write_config(config)
                with self.assertRaises(WorkspaceError):
                    create_workspace(**self.arguments)
                self.assertFalse(self.output_root.exists())

    def test_unsupported_instructions_plugins_and_credentials_are_rejected(self):
        for field in ["instructions", "mcp", "plugin", "auth", "providers", "secret"]:
            config = copy.deepcopy(self.config)
            config[field] = "plain-secret-sentinel"
            self.write_config(config)
            with self.assertRaises(WorkspaceError) as error:
                create_workspace(**self.arguments)
            self.assertNotIn("secret-sentinel", str(error.exception))

    def test_modified_or_symlinked_fixture_is_rejected(self):
        path = self.repository / "benchmark" / "toy" / "fixture" / "toolbox.py"
        original = path.read_bytes()
        path.write_bytes(original + b"# unauthorized edit\n")
        with self.assertRaisesRegex(WorkspaceError, "immutable manifest"):
            create_workspace(**self.arguments)
        path.unlink()
        other = self.root / "fixture-copy.py"
        other.write_bytes(original)
        path.symlink_to(other)
        with self.assertRaisesRegex(WorkspaceError, "without symlinks"):
            create_workspace(**self.arguments)
        self.assertFalse(self.output_root.exists())

    def test_path_traversal_and_symlink_destinations_are_rejected(self):
        for field, value in [("run_id", "../escape"), ("provider", "../escape"), ("model", "invalid\nmodel")]:
            arguments = {**self.arguments, field: value}
            with self.assertRaises(WorkspaceError):
                create_workspace(**arguments)
        target = self.root / "real-output"
        target.mkdir()
        self.output_root.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(WorkspaceError, "symlinks"):
            create_workspace(**self.arguments)
        self.assertEqual(list(target.iterdir()), [])

    def test_output_inside_benchmark_and_symlink_config_are_rejected(self):
        with self.assertRaisesRegex(WorkspaceError, "outside the benchmark"):
            create_workspace(**{**self.arguments, "output_root": self.repository / "workspaces"})
        alias = self.root / "config-link.json"
        alias.symlink_to(self.config_path)
        with self.assertRaisesRegex(WorkspaceError, "without symlinks"):
            create_workspace(**{**self.arguments, "config_path": alias})

    def test_failed_git_preparation_removes_only_its_new_directory(self):
        with patch("scripts.create_workspace.git", side_effect=WorkspaceError("synthetic Git failure")):
            with self.assertRaises(WorkspaceError):
                create_workspace(**self.arguments)
        self.assertFalse((self.output_root / "toy" / "test-provider" / "001").exists())
        workspace, _ = create_workspace(**self.arguments)
        self.assertTrue((workspace / ".git").is_dir())

    def test_identical_inputs_have_reproducible_baseline_commits(self):
        first_workspace, first_metadata = create_workspace(**self.arguments)
        second_workspace, second_metadata = create_workspace(**{**self.arguments, "run_id": "002"})
        self.assertEqual(git(first_workspace, "rev-parse", "HEAD"), git(second_workspace, "rev-parse", "HEAD"))
        self.assertEqual(json.loads(first_metadata.read_text())["task_snapshot_sha256"],
                         json.loads(second_metadata.read_text())["task_snapshot_sha256"])

    def test_default_config_selection_and_model_ids_with_slashes(self):
        selected = self.repository / "providers" / "test-provider" / "opencode.json"
        selected.parent.mkdir(parents=True)
        self.config["model"] = "test-provider/family/test-model"
        self.config["small_model"] = self.config["model"]
        self.config["provider"]["test-provider"]["models"] = {"family/test-model": {}}
        selected.write_text(json.dumps(self.config))
        workspace, metadata_path = create_workspace(**{**self.arguments, "config_path": None, "model": "family/test-model"})
        self.assertEqual((workspace / "opencode.json").read_bytes(), selected.read_bytes())
        self.assertEqual(json.loads(metadata_path.read_text())["model_id"], "family/test-model")

    def test_missing_malformed_duplicate_and_nonfinite_config_are_rejected(self):
        for data in [b"{", b'{"model": "x", "model": "test-provider/test-model"}', b'{"model": "test-provider/test-model", "timeout": NaN}']:
            self.config_path.write_bytes(data)
            with self.assertRaises(WorkspaceError):
                create_workspace(**self.arguments)
        self.config_path.unlink()
        with self.assertRaisesRegex(WorkspaceError, "--config"):
            create_workspace(**self.arguments)

    def test_cli_prepares_workspace_without_calling_opencode(self):
        result = subprocess.run(
            [shutil.which("python3"), str(REPOSITORY_ROOT / "scripts" / "create_workspace.py"),
             "--benchmark", "toy", "--provider", "test-provider", "--model", "test-model",
             "--run-id", "cli", "--config", str(self.config_path), "--output-root", str(self.output_root)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertTrue(Path(output["workspace"]).is_dir())
        self.assertTrue(Path(output["metadata"]).is_file())


if __name__ == "__main__":
    unittest.main()
