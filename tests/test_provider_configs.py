"""Offline provider-profile integration checks; no authentication or API calls."""

import copy
import fnmatch
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.create_workspace import REPOSITORY_ROOT, WorkspaceError, create_workspace, validate_config


class ProviderConfigTests(unittest.TestCase):
    def setUp(self):
        self.profiles = []
        for provider in ("nvidia", "mistral", "albert", "aristote"):
            directory = REPOSITORY_ROOT / "providers" / provider
            metadata = json.loads((directory / "metadata.json").read_text())
            for filename in metadata["configs"]:
                path = directory / filename
                self.profiles.append((provider, path, json.loads(path.read_text()), metadata))

    def test_profile_identity_hashes_and_evidence_are_consistent(self):
        for provider, path, config, metadata in self.profiles:
            with self.subTest(profile=str(path)):
                filename = path.relative_to(REPOSITORY_ROOT / "providers" / provider).as_posix()
                model = metadata["configs"][filename]["model_id"]
                validate_config(path.read_bytes(), provider, model)
                self.assertEqual(config["model"], f"{provider}/{model}")
                self.assertEqual(config["small_model"], config["model"])
                self.assertEqual(metadata["configs"][filename]["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
                matching = [entry for entry in metadata["models"] if entry["model_id"] == model]
                self.assertEqual(len(matching), 1)
                self.assertIsNone(matching[0]["checkpoint_revision"])
                if provider in {"albert", "aristote", "mistral"}:
                    self.assertEqual(matching[0]["authenticated_availability"], "owner_authenticated_catalog_snapshot")
                else:
                    self.assertIsNone(matching[0]["authenticated_availability"])
                self.assertEqual(matching[0]["checkpoint_status"], "model-family-only")
                self.assertFalse(metadata["network_policy"]["scored_ready"])

    def test_defaults_preserve_all_four_existing_connect_connections(self):
        for provider, path, config, metadata in self.profiles:
            options = config["provider"][provider]["options"]
            self.assertNotIn("apiKey", options)
            self.assertNotIn("headers", options)
            self.assertEqual(metadata["authentication"]["mode"], "opencode_managed_persistent_credential")
            self.assertIsNone(metadata["authentication"]["credential_storage_location"])
            self.assertIsNone(metadata["authentication"]["credential_present_usable"])
            text = path.read_text()
            self.assertNotIn("nvapi-", text)
            self.assertNotIn("sk-", text)
            self.assertNotIn("{file:", text)

    def test_all_agent_executable_and_web_routes_are_denied(self):
        for _, path, config, _ in self.profiles:
            with self.subTest(profile=str(path)):
                self.assertEqual(config["permission"]["*"], "deny")
                for tool in ("webfetch", "websearch", "bash", "task", "skill", "lsp"):
                    self.assertIs(config["tools"][tool], False)
                    self.assertEqual(config["permission"][tool], "deny")
                self.assertIs(config["formatter"], False)
                self.assertIs(config["lsp"], False)
                self.assertEqual(config["mcp"], {})
                self.assertEqual(config["plugin"], [])
                self.assertIs(config["autoupdate"], False)
                self.assertEqual(config["share"], "disabled")

    def test_agents_can_edit_code_but_cannot_reconfigure_their_tools(self):
        for _, path, config, _ in self.profiles:
            rules = config["permission"]["edit"]
            def permission(filename):
                result = "deny"
                for pattern, action in rules.items():
                    if fnmatch.fnmatchcase(filename, pattern):
                        result = action
                return result
            with self.subTest(profile=str(path)):
                self.assertEqual(permission("/workspace/toolbox.py"), "allow")
                self.assertEqual(permission("/workspace/test_word_frequency.py"), "allow")
                for filename in ["/workspace/opencode.json", "/workspace/opencode.jsonc", "/workspace/.opencode/tools/network.ts", "/workspace/.git/config", "/workspace/.git/hooks/pre-commit", "/workspace/.env", "/workspace/auth.json"]:
                    self.assertEqual(permission(filename), "deny", filename)

    def test_every_profile_can_prepare_an_allowlisted_workspace(self):
        with tempfile.TemporaryDirectory() as root:
            for number, (provider, path, config, _) in enumerate(self.profiles):
                model = config["model"].split("/", 1)[1]
                workspace, metadata_path = create_workspace(
                    benchmark="toy", provider=provider, model=model, run_id=f"profile-{number}",
                    config_path=path, output_root=Path(root) / "workspaces",
                )
                self.assertEqual((workspace / "opencode.json").read_bytes(), path.read_bytes())
                self.assertEqual({p.name for p in workspace.iterdir()}, {"toolbox.py", "test_toolbox.py", "opencode.json", ".git"})
                self.assertNotIn(workspace, metadata_path.parents)

    def test_validator_rejects_network_integrations_or_routing_reenabled(self):
        provider, _, original, _ = self.profiles[0]
        changes = [
            ("enabled_providers", [provider, "foreign"]),
            ("mcp", {"network": {"type": "remote", "url": "https://example.invalid"}}),
            ("plugin", ["network-plugin"]), ("formatter", True), ("lsp", True),
            ("permission", {"bash": "allow"}), ("tools", {"webfetch": True}),
            ("permission", {"edit": {"*": "allow"}}),
        ]
        for key, value in changes:
            config = copy.deepcopy(original)
            config[key] = value
            with self.subTest(key=key):
                with self.assertRaises(WorkspaceError):
                    validate_config(json.dumps(config).encode(), provider, config["model"].split("/", 1)[1])

    def test_validator_rejects_wildcard_allow_after_protective_denials(self):
        provider, _, original, _ = self.profiles[0]
        for tool in ("read", "edit"):
            config = copy.deepcopy(original)
            rules = config["permission"][tool]
            wildcard = rules.pop("*")
            rules["*"] = wildcard
            with self.subTest(tool=tool):
                with self.assertRaises(WorkspaceError):
                    validate_config(json.dumps(config).encode(), provider, config["model"].split("/", 1)[1])


if __name__ == "__main__":
    unittest.main()
