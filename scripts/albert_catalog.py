"""Offline parsing of the owner's sanitized Albert catalog; never authenticate."""

import hashlib
import math
from pathlib import Path

if __package__:
    from scripts.create_workspace import WorkspaceError, load_json, read_regular_file
else:
    from create_workspace import WorkspaceError, load_json, read_regular_file


SNAPSHOT = Path(__file__).resolve().parents[1] / "providers/albert/catalog-snapshots/2026-10-08.json"
PRIMARY = (
    "qwen3-coder-30b-a3b-instruct", "gpt-oss-120b", "deepseek-v4-flash-0731",
    "mistral-small-3-2-24b-instruct-2506",
)
OPTIONAL = ("ministral-3-8b-instruct-2512", "gemma-4-31b-it")
EXCLUDED = {
    "bge-m3": "Embedding model; not a conversational coding agent.",
    "bge-reranker-v2-m3": "Reranking model; not a conversational coding agent.",
    "qwen3-vl-embedding-8b": "Embedding model; not a conversational coding agent.",
    "whisper-large-v3": "Automatic speech recognition; not a coding agent.",
    "lightonocr-2-1b": "OCR-specialized model; image-text type alone does not establish coding suitability.",
}


def parse_catalog(data):
    catalog = load_json(data)
    if not isinstance(catalog, dict) or catalog.get("object") != "list" or not isinstance(catalog.get("data"), list):
        raise WorkspaceError("Albert catalog must be an object=list with a data array.")
    models = {}
    aliases = set()
    for entry in catalog["data"]:
        if not isinstance(entry, dict):
            raise WorkspaceError("Invalid Albert model entry.")
        if not {"object", "id", "aliases", "type", "owned_by", "max_context_length", "costs"} <= entry.keys():
            raise WorkspaceError("Incomplete Albert catalog entry.")
        model_id = entry["id"]
        if entry["object"] != "model" or not isinstance(model_id, str) or not model_id or model_id in models:
            raise WorkspaceError("Invalid or duplicate canonical Albert ID.")
        if any(not isinstance(entry[key], str) or not entry[key] for key in ("type", "owned_by")):
            raise WorkspaceError("Invalid Albert catalog type/operator.")
        names = entry["aliases"]
        if not isinstance(names, list) or any(not isinstance(name, str) or not name for name in names) or len(names) != len(set(names)):
            raise WorkspaceError("Invalid Albert aliases.")
        if aliases.intersection(names):
            raise WorkspaceError("Ambiguous Albert aliases.")
        aliases.update(names)
        context = entry["max_context_length"]
        if context is not None and (type(context) is not int or context <= 0):
            raise WorkspaceError("Invalid Albert context declaration.")
        costs = entry["costs"]
        if not isinstance(costs, dict) or not {"prompt_tokens", "completion_tokens"} <= costs.keys():
            raise WorkspaceError("Missing advertised Albert token costs.")
        for cost in (costs["prompt_tokens"], costs["completion_tokens"]):
            if cost is not None and (type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0):
                raise WorkspaceError("Invalid advertised Albert token cost.")
        models[model_id] = entry
    if set(models).intersection(aliases):
        raise WorkspaceError("Canonical Albert IDs must not also be aliases.")
    return models


def candidate_status(entry):
    model_id = entry["id"]
    if model_id in EXCLUDED:
        return "excluded", EXCLUDED[model_id]
    if entry["type"] not in {"text-generation", "image-text-to-text"}:
        return "excluded", "Model type cannot support conversational coding tasks."
    if model_id in PRIMARY:
        return "priority", None
    if model_id in OPTIONAL:
        return "optional", None
    return "unreviewed", "New catalog entry requires explicit human candidate review."


def canonical_candidate(models, model_id):
    """Never resolve aliases or silently promote unreviewed catalog entries."""
    if model_id not in models:
        raise WorkspaceError("Albert model must be a canonical catalog ID, never an alias.")
    status, _ = candidate_status(models[model_id])
    if status not in {"priority", "optional"}:
        raise WorkspaceError("Albert model is excluded or not reviewed for coding trials.")
    return models[model_id]


def read_catalog(path=SNAPSHOT):
    data = read_regular_file(path)
    return parse_catalog(data), hashlib.sha256(data).hexdigest()
