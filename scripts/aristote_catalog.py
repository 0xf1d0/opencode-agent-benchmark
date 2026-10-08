"""Offline owner-catalog validation; raw API fields do not establish semantics."""

import hashlib
from pathlib import Path

if __package__:
    from scripts.create_workspace import WorkspaceError, load_json, read_regular_file
else:
    from create_workspace import WorkspaceError, load_json, read_regular_file


SNAPSHOT = Path(__file__).resolve().parents[1] / "providers/aristote/catalog-snapshots/2026-10-08.json"
PRIMARY = (
    "qwen-3.6-35b-instruct", "qwen-3.6-35b-instruct-reasoning-high",
    "qwen-3.8-27b", "mistral-small-3.2-24b", "mistral-small-4-119b",
)
OPTIONAL = ("gemma-4-31b", "llama-3.1-8b")
FLOATING = "mistral-medium-latest"


def parse_catalog(data):
    catalog = load_json(data)
    if not isinstance(catalog, dict) or not isinstance(catalog.get("data"), list):
        raise WorkspaceError("Aristote catalog must contain a data array.")
    if "object" in catalog and catalog["object"] != "list":
        raise WorkspaceError("Invalid Aristote catalog object type.")
    models = {}
    for entry in catalog["data"]:
        if not isinstance(entry, dict):
            raise WorkspaceError("Aristote model records must be objects.")
        model_id = entry.get("id")
        if not isinstance(model_id, str) or not model_id or model_id != model_id.strip() or model_id in models:
            raise WorkspaceError("Invalid or duplicate canonical Aristote ID.")
        if "object" in entry and entry["object"] != "model":
            raise WorkspaceError("Invalid Aristote model object type.")
        if entry.get("mode") is not None and not isinstance(entry["mode"], str):
            raise WorkspaceError("Invalid Aristote mode declaration.")
        # Preserve all raw fields, including absent mode. Do not synthesize aliases,
        # reinterpret owned_by/created or require undocumented optional fields.
        models[model_id] = entry
    return models


def candidate_status(entry):
    mode = entry.get("mode")
    if mode in {"embedding", "rerank"}:
        return "excluded", f"Catalog mode {mode}; not a conversational coding-agent model."
    if entry["id"] in {"bge-m3", "bge-reranker-v2-m3"}:
        return "excluded", "Non-coding service model; conversational eligibility is not established."
    if entry["id"] == FLOATING:
        return "floating_alias", "Floating ID; immutable underlying served version is unverified."
    if mode not in {None, "chat"}:
        return "unreviewed", "Service mode requires explicit human review."
    if entry["id"] in PRIMARY:
        return "priority", None
    if entry["id"] in OPTIONAL:
        return "optional", None
    return "unreviewed", "New canonical ID requires explicit human candidate review."


def canonical_candidate(models, model_id):
    if model_id not in models:
        raise WorkspaceError("Aristote model must be an exact canonical catalog ID; aliases are not resolved.")
    if candidate_status(models[model_id])[0] not in {"priority", "optional"}:
        raise WorkspaceError("Aristote model is excluded, floating or not reviewed for coding trials.")
    return models[model_id]


def read_catalog(path=SNAPSHOT):
    data = read_regular_file(path)
    return parse_catalog(data), hashlib.sha256(data).hexdigest()
