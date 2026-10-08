"""Deterministic infrastructure checks; only the unsolved public baseline runs."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from scripts.create_workspace import REPOSITORY_ROOT


def minimal_record(schema, root):
    """Synthetic missing-data record for schema regressions, not a run result."""
    if "$ref" in schema:
        return minimal_record(root["$defs"][schema["$ref"].split("/")[-1]], root)
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return None if None in schema["enum"] else schema["enum"][0]
    types = schema.get("type", [])
    if types == "null" or isinstance(types, list) and "null" in types:
        return None
    if "anyOf" in schema:
        options = schema["anyOf"]
        option = next((item for item in options if item.get("type") == "null"), options[0])
        return minimal_record(option, root)
    if types == "object":
        return {key: minimal_record(schema["properties"][key], root) for key in schema["required"]}
    if types == "array":
        return []
    if types == "string":
        return "synthetic"
    if types == "integer":
        return schema.get("minimum", 0)
    if types == "boolean":
        return False
    raise AssertionError("Unhandled synthetic schema shape")


class RepositoryIntegrityTests(unittest.TestCase):
    def test_immutable_fixture_hashes(self):
        directory = REPOSITORY_ROOT / "benchmark/toy"
        manifest = json.loads((directory / "fixture_manifest.json").read_text())
        self.assertEqual(set(manifest["files"]), {"toolbox.py", "test_toolbox.py"})
        for filename, expected in manifest["files"].items():
            self.assertEqual(hashlib.sha256((directory / "fixture" / filename).read_bytes()).hexdigest(), expected)

    def test_prompt_bytes_hashes_provenance_and_independent_conditions(self):
        directory = REPOSITORY_ROOT / "benchmark/toy/prompts"
        metadata = json.loads((directory / "metadata.json").read_text())
        self.assertEqual(metadata["prompt_set_version"], "1.0.0")
        self.assertEqual([entry["id"] for entry in metadata["prompts"]], metadata["prompt_order"])
        self.assertIn("same declared snapshot", metadata["execution_notes"][0])
        files = set()
        for entry in metadata["prompts"] + metadata["workflow_commands"]:
            data = (directory / entry["file"]).read_bytes()
            text = data.decode("utf-8")
            files.add(entry["file"])
            self.assertTrue(data.endswith(b"\n"))
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])
            for forbidden in ("nvidia", "mistral", "albert", "aristote", "glm-5", "gpt-oss"):
                self.assertNotIn(forbidden, text.lower())
            self.assertIn(entry["origin"], metadata["origin_definitions"])
            self.assertIn("tp_reference", entry)
        self.assertEqual(files, {path.name for path in directory.glob("*.txt")})

    def test_all_schemas_have_valid_metaschemas_and_documented_fields(self):
        def descriptions(value):
            if isinstance(value, dict):
                if value.get("type") == "object":
                    for key, field in value.get("properties", {}).items():
                        self.assertTrue(field.get("description"), key)
                for field in value.values():
                    descriptions(field)
            elif isinstance(value, list):
                for field in value:
                    descriptions(field)
        for path in (REPOSITORY_ROOT / "schemas").glob("*.schema.json"):
            with self.subTest(schema=path.name):
                schema = json.loads(path.read_text())
                Draft202012Validator.check_schema(schema)
                descriptions(schema)

    def test_result_missing_values_review_justification_and_hidden_boundary(self):
        schema = json.loads((REPOSITORY_ROOT / "schemas/result.schema.json").read_text())
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        record = minimal_record(schema, schema)
        validator.validate(record)
        record["number_of_attempts"] = "unknown"
        with self.assertRaises(ValidationError):
            validator.validate(record)
        interaction_schema = schema["$defs"]["interaction"]
        interaction = minimal_record(interaction_schema, schema)
        interaction["decision"] = "accepted"
        iv = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/interaction"})
        with self.assertRaises(ValidationError):
            iv.validate(interaction)
        interaction["decision_justification"] = "Synthetic human-review evidence reference."
        interaction["review_phase"] = "post_run"
        iv.validate(interaction)
        hidden = minimal_record(schema["$defs"]["test_run"], schema)
        hidden["phase"] = "agent"
        hv = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/hidden_test_run"})
        with self.assertRaises(ValidationError):
            hv.validate(hidden)
        hidden["phase"] = "evaluation"
        hv.validate(hidden)

    def test_public_baseline_is_exactly_two_passes_and_one_intended_failure(self):
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            for filename in ("toolbox.py", "test_toolbox.py"):
                shutil.copyfile(REPOSITORY_ROOT / "benchmark/toy/fixture" / filename, directory / filename)
            report = directory / "report.xml"
            # No inherited key-bearing environment or OpenCode/private state.
            environment = {"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "LANG": "C.UTF-8"}
            result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml", str(report), "test_toolbox.py"], cwd=directory, env=environment, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            cases = ET.parse(report).findall(".//testcase")
            self.assertEqual(len(cases), 3)
            failures = [case.attrib["name"] for case in cases if case.find("failure") is not None]
            self.assertEqual(failures, ["test_is_palindrome_with_spaces"])
            self.assertEqual(sum(case.find("failure") is None and case.find("error") is None and case.find("skipped") is None for case in cases), 2)

    def test_generated_artifacts_are_ignored(self):
        paths = ["benchmark/toy/fixture/__pycache__/example.pyc", ".pytest_cache/x", ".mypy_cache/x", ".ruff_cache/x", ".coverage", "htmlcov/x", ".venv/x", "workspaces/x", "runs/x", "cache/x"]
        result = subprocess.run(["git", "check-ignore", "--no-index", "--stdin"], cwd=REPOSITORY_ROOT, input="\n".join(paths) + "\n", capture_output=True, text=True, env={"PATH": os.defpath, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}, check=True)
        self.assertEqual(set(result.stdout.splitlines()), set(paths))
