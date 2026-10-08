#!/usr/bin/env python3
"""Create/check offline Level 1 runtime locks; never invoke OpenCode or an API."""

import argparse
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
import importlib
import json
from pathlib import Path
import platform
import sys

if __package__:
    from scripts.create_workspace import REPOSITORY_ROOT, WorkspaceError, digest, git, load_json, read_regular_file, validate_config
else:
    from create_workspace import REPOSITORY_ROOT, WorkspaceError, digest, git, load_json, read_regular_file, validate_config


def validate_schema(record, filename):
    from jsonschema import Draft202012Validator, FormatChecker
    schema = load_json(read_regular_file(REPOSITORY_ROOT / "schemas" / filename))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    if next(validator.iter_errors(record), None) is not None:
        raise WorkspaceError("Record does not satisfy its versioned schema.")


def installed_version(name):
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def build_lock(*, provider, model, prompt_id, run_id, campaign_id, opencode_version,
               observed_opencode_version=None, opencode_artifact_sha256=None,
               runtime_image=None, sandbox_review_id=None):
    if provider not in {"nvidia", "mistral", "albert", "aristote"}:
        raise WorkspaceError("Unknown project provider.")
    directory = REPOSITORY_ROOT / "providers" / provider
    metadata_bytes = read_regular_file(directory / "metadata.json")
    metadata = load_json(metadata_bytes)
    matches = [filename for filename, config in metadata["configs"].items() if config["model_id"] == model]
    if len(matches) != 1:
        raise WorkspaceError("Select one registered canonical provider/model cell.")
    config_path = directory / matches[0]
    if directory not in config_path.resolve().parents:
        raise WorkspaceError("Configuration must be inside its provider directory.")
    config_bytes = read_regular_file(config_path)
    validate_config(config_bytes, provider, model)
    if digest(config_bytes) != metadata["configs"][matches[0]]["sha256"]:
        raise WorkspaceError("Provider configuration hash differs from metadata.")
    catalog_sha = None
    if provider in {"albert", "aristote", "mistral"}:
        catalog_module = importlib.import_module(("scripts." if __package__ else "") + provider + "_catalog")
        models, catalog_sha = catalog_module.read_catalog()
        catalog_module.canonical_candidate(models, model)
        if catalog_sha != metadata["catalog"]["sha256"]:
            raise WorkspaceError("Provider catalog hash differs from its evidence card.")
    prompt_metadata_bytes = read_regular_file(REPOSITORY_ROOT / "benchmark/toy/prompts/metadata.json")
    prompts = load_json(prompt_metadata_bytes)
    selected = [prompt for prompt in prompts["prompts"] if prompt["id"] == prompt_id]
    if len(selected) != 1:
        raise WorkspaceError("Unknown or ambiguous frozen prompt ID.")
    prompt = selected[0]
    prompt_path = REPOSITORY_ROOT / "benchmark/toy/prompts" / prompt["file"]
    if prompt_path.parent.resolve() != (REPOSITORY_ROOT / "benchmark/toy/prompts").resolve():
        raise WorkspaceError("Prompt must be inside its declared directory.")
    if digest(read_regular_file(prompt_path)) != prompt["sha256"]:
        raise WorkspaceError("Prompt bytes differ from the frozen prompt hash.")
    fixture_bytes = read_regular_file(REPOSITORY_ROOT / "benchmark/toy/fixture_manifest.json")
    fixture = load_json(fixture_bytes)
    if set(fixture.get("files", {})) != {"toolbox.py", "test_toolbox.py"}:
        raise WorkspaceError("Fixture manifest must enumerate exactly the public fixture files.")
    for filename, sha in fixture["files"].items():
        if filename not in {"toolbox.py", "test_toolbox.py"} or digest(read_regular_file(REPOSITORY_ROOT / "benchmark/toy/fixture" / filename)) != sha:
            raise WorkspaceError("Immutable fixture validation failed.")
    status = git(REPOSITORY_ROOT, "status", "--porcelain", required=False)
    lock = {
        "schema_version": "1.0.0", "record_type": "campaign_runtime_lock",
        "run_id": run_id, "campaign_id": campaign_id, "benchmark_level": 1,
        "benchmark_commit": git(REPOSITORY_ROOT, "rev-parse", "HEAD", required=False),
        "benchmark_dirty": None if status is None else bool(status),
        "opencode_version": opencode_version, "observed_opencode_version": observed_opencode_version,
        "opencode_artifact_sha256": opencode_artifact_sha256, "autoupdate": False,
        "python_version": platform.python_version(), "pytest_version": installed_version("pytest"),
        "git_version": git(REPOSITORY_ROOT, "--version", required=False),
        "operating_system": platform.system() + " " + platform.release(),
        "runtime_image": runtime_image, "provider": provider, "model_id": model,
        "provider_config_path": config_path.relative_to(REPOSITORY_ROOT).as_posix(),
        "provider_config_sha256": digest(config_bytes), "provider_evidence_sha256": digest(metadata_bytes),
        "catalog_snapshot_sha256": catalog_sha, "fixture_version": fixture["fixture_version"],
        "fixture_manifest_sha256": digest(fixture_bytes),
        "prompt_set_version": prompts["prompt_set_version"], "prompt_id": prompt_id,
        "prompt_sha256": prompt["sha256"], "prompt_metadata_sha256": digest(prompt_metadata_bytes),
        "requirements_sha256": digest(read_regular_file(REPOSITORY_ROOT / "requirements-dev.txt")),
        "requirements_resolved_sha256": digest(read_regular_file(REPOSITORY_ROOT / "requirements-ci.lock")),
        "protocol_track": "restricted", "sandbox_review_id": sandbox_review_id,
        "preparation_environment_only": True,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    validate_schema(lock, "runtime-lock.schema.json")
    return lock


def check_lock(lock, *, for_scoring=False, preflight=None, lock_sha256=None):
    validate_schema(lock, "runtime-lock.schema.json")
    current = build_lock(
        provider=lock["provider"], model=lock["model_id"], prompt_id=lock["prompt_id"],
        run_id=lock["run_id"], campaign_id=lock["campaign_id"], opencode_version=lock["opencode_version"],
        observed_opencode_version=lock["observed_opencode_version"],
        opencode_artifact_sha256=lock["opencode_artifact_sha256"], runtime_image=lock["runtime_image"],
        sandbox_review_id=lock["sandbox_review_id"],
    )
    for field in current:
        if field != "created_at" and current[field] != lock[field]:
            raise WorkspaceError("Runtime lock differs from current preparation provenance.")
    if for_scoring:
        if lock["benchmark_dirty"] is not False or lock["benchmark_commit"] is None:
            raise WorkspaceError("Scoring requires a clean committed benchmark source.")
        if lock["observed_opencode_version"] != lock["opencode_version"]:
            raise WorkspaceError("Observed OpenCode release must match the pinned version.")
        if any(lock[field] is None for field in ("pytest_version", "git_version", "opencode_artifact_sha256", "sandbox_review_id")):
            raise WorkspaceError("Scoring requires recorded runtime dependencies, OpenCode artifact and isolation audit.")
        if preflight is None:
            raise WorkspaceError("Scoring requires an owner-driven preflight record.")
        validate_schema(preflight, "preflight.schema.json")
        if not preflight["scored_ready"]:
            raise WorkspaceError("Provider/model preflight is not scored-ready.")
        expected_hash = lock_sha256 or digest((json.dumps(lock, indent=2) + "\n").encode())
        if preflight["runtime_lock_sha256"] != expected_hash:
            raise WorkspaceError("Preflight must reference the exact runtime-lock bytes.")
        for field in ("provider", "model_id", "protocol_track"):
            if preflight[field] != lock[field]:
                raise WorkspaceError("Preflight cell or track differs from its runtime lock.")
        if preflight["authentication"]["provider_id"] != lock["provider"] or preflight["observed_provider"] != lock["provider"] or preflight["observed_model_id"] != lock["model_id"]:
            raise WorkspaceError("Preflight authentication and observed routing must match the exact cell.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    for name in ("provider", "model", "prompt-id", "run-id", "campaign-id", "opencode-version"):
        create.add_argument("--" + name, required=True)
    for name in ("observed-opencode-version", "opencode-artifact-sha256", "runtime-image", "sandbox-review-id"):
        create.add_argument("--" + name)
    create.add_argument("--output", type=Path, required=True)
    check = commands.add_parser("check")
    check.add_argument("--manifest", type=Path, required=True)
    check.add_argument("--for-scoring", action="store_true")
    check.add_argument("--preflight", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            arguments = vars(args).copy()
            arguments.pop("command")
            output = arguments.pop("output")
            record = build_lock(**arguments)
            with output.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(record, indent=2) + "\n")
            output.chmod(0o600)
        else:
            lock_bytes = read_regular_file(args.manifest)
            lock = load_json(lock_bytes)
            preflight = load_json(read_regular_file(args.preflight)) if args.preflight else None
            check_lock(lock, for_scoring=args.for_scoring, preflight=preflight, lock_sha256=digest(lock_bytes))
    except (WorkspaceError, OSError) as error:
        parser.exit(1, "error: " + (str(error) if isinstance(error, WorkspaceError) else "Filesystem operation failed.") + "\n")
    print("Offline runtime-lock validation completed; no OpenCode or provider call was made.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
