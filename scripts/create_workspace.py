#!/usr/bin/env python3
"""Prepare a secret-free Level 1 workspace; never start an agent or call an API."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FILES = ("toolbox.py", "test_toolbox.py")
ENV_REFERENCE = re.compile(r"\{env:[A-Za-z_][A-Za-z0-9_]*\}")
COMPONENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
MODEL_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}")
OFFLINE_READ_RULES = {
    "*": "allow", "*.env": "deny", "*.env.*": "deny",
    "*auth.json": "deny", "*credentials*": "deny",
}
OFFLINE_EDIT_RULES = {
    "*": "allow", "*opencode.json": "deny", "*opencode.jsonc": "deny",
    ".opencode/*": "deny", "*/.opencode/*": "deny",
    ".git/*": "deny", "*/.git/*": "deny", "*.env": "deny",
    "*.env.*": "deny", "*auth.json": "deny", "*credentials*": "deny",
}
GIT_ENV = {
    "PATH": os.defpath,
    "LANG": "C.UTF-8",
    "TZ": "UTC",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_NO_REPLACE_OBJECTS": "1",
    "GIT_AUTHOR_NAME": "Benchmark baseline",
    "GIT_AUTHOR_EMAIL": "benchmark@invalid",
    "GIT_COMMITTER_NAME": "Benchmark baseline",
    "GIT_COMMITTER_EMAIL": "benchmark@invalid",
    # Canonical construction timestamp; actual preparation time goes in metadata.
    "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+00:00",
    "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+00:00",
}


class WorkspaceError(Exception):
    """A preparation failure that can be reported without disclosing secrets."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_regular_file(path):
    """Refuse symlinks, including parent-directory aliases, and special files."""
    path = Path(os.path.abspath(path))
    if path.resolve() != path or not stat.S_ISREG(path.lstat().st_mode):
        raise WorkspaceError("Input must be a regular file without symlinks.")
    return path.read_bytes()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise WorkspaceError("JSON contains duplicate object keys.")
        result[key] = value
    return result


def reject_constant(_value):
    raise WorkspaceError("JSON must not contain non-finite numeric constants.")


def load_json(data):
    try:
        return json.loads(
            data.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError):
        raise WorkspaceError("Input must be strict UTF-8 JSON, not JSONC.") from None


def check_keys(value, allowed):
    if not isinstance(value, dict) or set(value) - set(allowed):
        # Do not include unknown keys/values: they might themselves be secrets.
        raise WorkspaceError("Configuration contains unsupported fields.")


def check_text(value):
    if not isinstance(value, str) or not value or len(value) > 512:
        raise WorkspaceError("Configuration text is invalid.")
    if "{file:" in value or "{env:" in value:
        raise WorkspaceError("References are permitted only in credential fields.")
    if re.search(r"(?:\bsk[-_]|\bBearer\s|\beyJ[A-Za-z0-9_-]+\.)", value):
        raise WorkspaceError("Configuration contains possible embedded credentials.")
    if any(ord(char) < 32 for char in value):
        raise WorkspaceError("Configuration text contains control characters.")


def check_positive_integer(value):
    if type(value) is not int or value <= 0:
        raise WorkspaceError("Configuration limit/timeout must be a positive integer.")


def check_credential_reference(value, bearer=False):
    if not isinstance(value, str):
        raise WorkspaceError("Credentials must use an unresolved environment reference.")
    if bearer and value.startswith("Bearer "):
        value = value[len("Bearer "):]
    if not ENV_REFERENCE.fullmatch(value):
        raise WorkspaceError("Literal credentials and file references are forbidden.")


def check_options(options):
    check_keys(options, {"baseURL", "apiKey", "headers", "timeout", "chunkTimeout"})
    for key, value in options.items():
        if key == "apiKey":
            check_credential_reference(value)
        elif key == "headers":
            if not isinstance(value, dict):
                raise WorkspaceError("Configuration headers must be an object.")
            for header, content in value.items():
                if not re.fullmatch(r"[A-Za-z0-9-]+", header):
                    raise WorkspaceError("Invalid header name.")
                if header.lower() in {"accept", "content-type"} and content == "application/json":
                    continue
                check_credential_reference(content, bearer=header.lower() == "authorization")
        elif key == "baseURL":
            check_text(value)
            try:
                url = urlsplit(value)
                valid = (
                    url.scheme in {"http", "https"} and url.hostname
                    and not url.username and not url.password
                    and not url.query and not url.fragment
                )
                url.port  # Validate malformed port syntax as well.
            except ValueError:
                valid = False
            if not valid:
                raise WorkspaceError("Endpoint must not contain credentials, query or fragment.")
        else:
            check_positive_integer(value)


def validate_config(data, provider, model):
    """Accept a narrow, secret-free OpenCode v1 config and preserve its bytes."""
    config = load_json(data)
    check_keys(config, {"$schema", "model", "small_model", "provider", "autoupdate", "compaction", "tools", "permission", "share", "enabled_providers", "mcp", "plugin", "lsp", "formatter"})
    selected = f"{provider}/{model}"
    if config.get("model") != selected:
        raise WorkspaceError("Configuration model must exactly match --provider/--model.")
    if "small_model" in config and config["small_model"] != selected:
        raise WorkspaceError("Auxiliary model must match the selected provider/model.")
    if "$schema" in config and config["$schema"] != "https://opencode.ai/config.json":
        raise WorkspaceError("Unsupported OpenCode configuration schema URL.")
    if "autoupdate" in config and config["autoupdate"] is not False:
        raise WorkspaceError("Automatic updates must be disabled.")
    if "share" in config and config["share"] != "disabled":
        raise WorkspaceError("Automatic sharing must be disabled.")
    if "enabled_providers" in config and config["enabled_providers"] != [provider]:
        raise WorkspaceError("Only the selected provider may be enabled.")
    for key, required_value in {"mcp": {}, "plugin": [], "lsp": False, "formatter": False}.items():
        if key in config and (type(config[key]) is not type(required_value) or config[key] != required_value):
            raise WorkspaceError("Executable integrations must be disabled.")
    if "provider" in config:
        providers = config["provider"]
        check_keys(providers, {provider})
        if set(providers) != {provider}:
            raise WorkspaceError("Configuration must declare only the selected provider.")
        definition = providers[provider]
        check_keys(definition, {"npm", "name", "options", "models"})
        if "npm" in definition and definition["npm"] not in {
            "@ai-sdk/openai-compatible", "@ai-sdk/openai", "@ai-sdk/mistral",
        }:
            raise WorkspaceError("Unsupported provider adapter; file/package references are forbidden.")
        if "name" in definition:
            check_text(definition["name"])
        if "options" in definition:
            check_options(definition["options"])
        if "models" in definition:
            check_keys(definition["models"], {model})
            if set(definition["models"]) != {model}:
                raise WorkspaceError("Configuration must declare only the selected model.")
            model_config = definition["models"][model]
            check_keys(model_config, {"name", "limit"})
            if "name" in model_config:
                check_text(model_config["name"])
            if "limit" in model_config:
                check_keys(model_config["limit"], {"context", "output"})
                for value in model_config["limit"].values():
                    check_positive_integer(value)
    if "compaction" in config:
        check_keys(config["compaction"], {"auto", "prune", "reserved"})
        for key, value in config["compaction"].items():
            if key == "reserved":
                check_positive_integer(value)
            elif type(value) is not bool:
                raise WorkspaceError("Compaction flags must be booleans.")
    if "tools" in config:
        check_keys(config["tools"], {"task", "webfetch", "websearch", "bash", "skill", "lsp"})
        if any(value is not False for value in config["tools"].values()):
            raise WorkspaceError("Optional network/delegation tools may only be disabled.")
    if "permission" in config:
        check_keys(config["permission"], {
            "*", "external_directory", "webfetch", "websearch", "task", "bash", "skill", "lsp",
            "read", "edit", "glob", "grep", "todowrite", "question",
        })
        for key, value in config["permission"].items():
            if key in {"read", "edit"} and isinstance(value, dict):
                expected = OFFLINE_READ_RULES if key == "read" else OFFLINE_EDIT_RULES
                if value != expected or next(iter(value), None) != "*":
                    raise WorkspaceError("Only the audited offline file-access rules are supported.")
            elif key in {"read", "edit", "glob", "grep", "todowrite", "question"}:
                if value not in ("allow", "deny"):
                    raise WorkspaceError("Invalid local-tool permission.")
            elif value != "deny":
                raise WorkspaceError("External/network/executable permissions may only be denied.")


def git(directory, *arguments, required=True):
    executable = shutil.which("git", path=os.defpath)
    if executable is None:
        raise WorkspaceError("Git is required on the system executable path.")
    result = subprocess.run(
        [executable, "-c", "core.hooksPath=" + os.devnull,
         "-c", "core.autocrlf=false", "-c", "core.attributesFile=" + os.devnull,
         "-c", "core.excludesFile=" + os.devnull, "-c", "commit.gpgSign=false",
         "-c", "core.fsmonitor=false",
         "-c", "init.defaultObjectFormat=sha1", "-C", str(directory), *arguments],
        env=GIT_ENV, capture_output=True, text=True, check=False,
    )
    if result.returncode:
        if required:
            raise WorkspaceError("Git preparation command failed; no workspace was published.")
        return None
    return result.stdout.strip()


def create_workspace(*, benchmark, provider, model, run_id, config_path=None,
                     output_root=None, repository_root=REPOSITORY_ROOT):
    if benchmark != "toy":
        raise WorkspaceError("Only the toy benchmark is implemented.")
    if not COMPONENT.fullmatch(provider) or not COMPONENT.fullmatch(run_id):
        raise WorkspaceError("Provider and run ID must be safe single path components.")
    check_text(provider)
    if not MODEL_ID.fullmatch(model):
        raise WorkspaceError("Invalid model identifier.")
    check_text(model)
    if "codex" in provider.lower() or "codex" in model.lower():
        raise WorkspaceError("Codex must not participate in benchmark runs.")
    repository_root = Path(repository_root).resolve()
    catalog_sha256 = None
    if provider == "albert":
        if __package__:
            from scripts.albert_catalog import canonical_candidate, read_catalog
        else:
            from albert_catalog import canonical_candidate, read_catalog
        catalog_models, catalog_sha256 = read_catalog(
            repository_root / "providers/albert/catalog-snapshots/2026-10-08.json"
        )
        canonical_candidate(catalog_models, model)
        default_config = repository_root / "providers" / provider / model / "opencode.json"
    else:
        default_config = repository_root / "providers" / provider / "opencode.json"
    config_path = Path(config_path) if config_path else default_config
    try:
        config_bytes = read_regular_file(config_path)
    except FileNotFoundError:
        raise WorkspaceError("Selected config is missing; provide a secret-free JSON file with --config.") from None
    validate_config(config_bytes, provider, model)

    manifest_path = repository_root / "benchmark" / "toy" / "fixture_manifest.json"
    manifest_bytes = read_regular_file(manifest_path)
    manifest = load_json(manifest_bytes)
    if (not isinstance(manifest, dict) or set(manifest) != {"schema_version", "fixture_version", "files"}
            or manifest["schema_version"] != 1 or manifest["fixture_version"] != "1.0.0"
            or not isinstance(manifest["files"], dict) or set(manifest["files"]) != set(FIXTURE_FILES)):
        raise WorkspaceError("Unsupported fixture manifest.")
    files = {}
    for filename in FIXTURE_FILES:
        data = read_regular_file(repository_root / "benchmark" / "toy" / "fixture" / filename)
        if digest(data) != manifest["files"][filename]:
            raise WorkspaceError("Fixture differs from its immutable manifest; refusing to prepare.")
        files[filename] = data
    files["opencode.json"] = config_bytes

    output_root = Path(output_root) if output_root else Path(tempfile.gettempdir()) / "opencode-benchmark-workspaces"
    output_root = Path(os.path.abspath(output_root))
    if output_root.resolve() != output_root:
        raise WorkspaceError("Workspace output root must not use symlinks.")
    if output_root == repository_root or repository_root in output_root.parents:
        raise WorkspaceError("Workspace output root must be outside the benchmark repository.")
    run_directory = output_root / benchmark / provider / run_id
    if run_directory == repository_root or repository_root in run_directory.parents:
        raise WorkspaceError("Run directory must be outside the benchmark repository.")
    # Check existing parent aliases before mkdir; reserve atomically, never reuse.
    if run_directory.resolve() != run_directory:
        raise WorkspaceError("Workspace path must not use symlinks.")
    try:
        run_directory.mkdir(parents=True, mode=0o700, exist_ok=False)
    except FileExistsError:
        raise WorkspaceError("Run directory already exists; refusing to overwrite it.") from None
    workspace = run_directory / "workspace"
    try:
        workspace.mkdir(mode=0o700)
        for filename, data in files.items():
            with (workspace / filename).open("xb") as output:
                output.write(data)
            (workspace / filename).chmod(0o644)
        git(workspace, "init", "--quiet", "--initial-branch=main", "--template=")
        git(workspace, "add", "--", *files)
        git(workspace, "commit", "--quiet", "--no-gpg-sign", "-m", "Initialize immutable toy fixture")
        baseline_commit = git(workspace, "rev-parse", "HEAD")
        if git(workspace, "status", "--porcelain"):
            raise WorkspaceError("New workspace baseline is unexpectedly dirty.")
        hashes = {filename: digest(data) for filename, data in sorted(files.items())}
        snapshot = json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
        source_status = git(repository_root, "status", "--porcelain", required=False)
        metadata = {
            "schema_version": 1,
            "record_type": "workspace_initialization",
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "benchmark": benchmark, "provider": provider, "model_id": model,
            "model_family": None, "opencode_version": None, "run_id": run_id,
            "workspace": "workspace", "fixture_version": manifest["fixture_version"],
            "fixture_manifest_sha256": digest(manifest_bytes),
            "config_format": "opencode_v1", "config_sha256": digest(config_bytes),
            "catalog_snapshot_sha256": catalog_sha256,
            "track": "restricted", "scored_ready": False,
            "files": hashes, "task_snapshot_sha256": digest(snapshot),
            "snapshot_hash_method": "SHA-256 of compact sorted-key UTF-8 JSON mapping filenames to file SHA-256 digests",
            "benchmark_commit": git(repository_root, "rev-parse", "HEAD", required=False),
            "benchmark_dirty": None if source_status is None else bool(source_status),
            "baseline_commit": baseline_commit, "git_version": git(workspace, "--version"),
            "agents_md": [],
        }
        metadata_path = run_directory / "initial_metadata.json"
        with metadata_path.open("x", encoding="utf-8") as output:
            output.write(json.dumps(metadata, indent=2) + "\n")
        metadata_path.chmod(0o600)
    except Exception:
        # Only remove the directory atomically created by this invocation.
        shutil.rmtree(run_directory)
        raise
    return workspace, metadata_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True, choices=["toy"])
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--config", type=Path, help="Secret-free OpenCode v1 JSON; Albert defaults to providers/albert/<canonical-model>/opencode.json, others to providers/<provider>/opencode.json")
    parser.add_argument("--output-root", type=Path, help="External output directory; defaults to the system temporary directory/opencode-benchmark-workspaces")
    args = parser.parse_args(argv)
    try:
        workspace, metadata_path = create_workspace(
            benchmark=args.benchmark, provider=args.provider, model=args.model,
            run_id=args.run_id, config_path=args.config, output_root=args.output_root,
        )
    except (WorkspaceError, OSError) as error:
        # OSError can include arbitrary input values; report a generic message.
        message = str(error) if isinstance(error, WorkspaceError) else "Filesystem preparation failed."
        parser.exit(1, "error: " + message + "\n")
    print(json.dumps({"workspace": str(workspace), "metadata": str(metadata_path)}))
    return 0


if __name__ == "__main__":
    # Catalog helpers import this module too; preserve the same exception type
    # when this file is invoked directly rather than imported as a package.
    sys.modules.setdefault("create_workspace", sys.modules[__name__])
    sys.exit(main())
