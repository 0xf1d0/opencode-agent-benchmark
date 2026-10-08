"""Offline sparse NVIDIA catalog validation and explicit reviewed profile mapping."""

import hashlib
from pathlib import Path
import re

if __package__:
    from scripts.create_workspace import WorkspaceError, load_json, read_regular_file
else:
    from create_workspace import WorkspaceError, load_json, read_regular_file


SNAPSHOT = Path(__file__).resolve().parents[1] / "providers/nvidia/catalog-snapshots/2026-10-08.json"
PROFILE_DIRECTORIES = {
    "nvidia/nemotron-3-ultra-550b-a55b": "nvidia-nemotron-3-ultra-550b-a55b",
    "nvidia/nemotron-3.5-lightning-30b-a3b": "nvidia-nemotron-3.5-lightning-30b-a3b",
    "z-ai/glm-5.3": "z-ai-glm-5.3",
}
PRIMARY = tuple(PROFILE_DIRECTORIES)
FIRST_PREFLIGHT = PRIMARY[1]
OPTIONAL = (
    "nvidia/nemotron-3-super-120b-a12b", "deepseek-ai/deepseek-v4.1-flash",
    "moonshotai/kimi-k3", "moonshotai/kimi-k2.6", "poolside/laguna-xs-2.1",
)
COMPARISON = "google/gemma-4-31b-it"
# Explicit reviewed IDs, not a name-based filter applied to new/ambiguous entries.
# Sparse catalog has no capability field; these reasons describe ID evidence only.
EXCLUDED = {
    **{model: "Explicit embedding/retrieval service identifier; not a conversational coding cell." for model in (
        "nvidia/embed-qa-4", "nvidia/nemotron-3-embed-1b",
        "nvidia/llama-3.2-nv-embedqa-1b-v1", "nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1",
        "nvidia/llama-nemotron-embed-vl-1b-v2", "nvidia/nv-embedqa-mistral-7b-v2", "snowflake/arctic-embed-l",
    )},
    **{model: "Explicit guard/safety/topic-control service identifier; not a general coding cell." for model in (
        "meta/llama-guard-4-12b", "nvidia/llama-3.1-nemoguard-8b-content-safety",
        "nvidia/llama-3.1-nemoguard-8b-topic-control", "nvidia/llama-3.1-nemotron-safety-guard-8b-v3",
        "nvidia/nemotron-3.5-content-safety",
    )},
    "nvidia/nemotron-4-340b-reward": "Explicit reward-model identifier; not a conversational coding cell.",
    "nvidia/nemotron-parse": "Explicit parsing service identifier; outside the general coding matrix.",
    "nvidia/nemotron-parse-2.0": "Explicit parsing service identifier; outside the general coding matrix.",
    "nvidia/ai-synthetic-video-detector": "Explicit synthetic-video detection identifier; outside coding tasks.",
    "nvidia/riva-translate-4b-instruct": "Explicit translation service identifier; outside the general coding matrix.",
    "nvidia/riva-translate-4b-instruct-v2": "Explicit translation service identifier; outside the general coding matrix.",
}
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*")


def parse_catalog(data):
    catalog = load_json(data)
    if not isinstance(catalog, dict) or catalog.get("object") != "list" or not isinstance(catalog.get("data"), list):
        raise WorkspaceError("NVIDIA catalog must be object=list with a data array.")
    models = {}
    for entry in catalog["data"]:
        if not isinstance(entry, dict):
            raise WorkspaceError("NVIDIA model records must be objects.")
        model_id = entry.get("id")
        if not isinstance(model_id, str) or not IDENTIFIER.fullmatch(model_id) or model_id in models:
            raise WorkspaceError("Invalid or duplicate canonical NVIDIA ID.")
        if entry.get("object") != "model" or type(entry.get("created")) is not int:
            raise WorkspaceError("NVIDIA record requires object=model and integer raw created.")
        if not isinstance(entry.get("owned_by"), str) or not entry["owned_by"].strip():
            raise WorkspaceError("NVIDIA record requires a raw owned_by string.")
        models[model_id] = entry  # Preserve raw fields without synthesizing capabilities/aliases.
    return models


def candidate_status(entry):
    model_id = entry["id"]
    if model_id in EXCLUDED:
        return "excluded", EXCLUDED[model_id]
    if model_id in PRIMARY:
        return "priority", None
    if model_id in OPTIONAL:
        return "optional", "Reviewed optional candidate; no initial active profile."
    if model_id == COMPARISON:
        return "comparison_candidate", "Albert/NVIDIA shared family label; exact serving identity unverified."
    return "unreviewed", "Sparse catalog provides no capabilities; explicit candidate review required."


def canonical_candidate(models, model_id):
    if model_id not in models or candidate_status(models[model_id])[0] != "priority":
        raise WorkspaceError("Select an exact authenticated NVIDIA ID with an active reviewed profile.")
    return models[model_id]


def registered_profile(metadata, model_id):
    """Resolve only explicit mappings, never interpolate an API ID into a path."""
    if model_id not in PROFILE_DIRECTORIES:
        raise WorkspaceError("NVIDIA model has no active profile mapping.")
    if metadata.get("canonical_id_to_profile_directory") != PROFILE_DIRECTORIES:
        raise WorkspaceError("NVIDIA canonical-to-directory registry differs from reviewed policy.")
    relative = PROFILE_DIRECTORIES[model_id] + "/opencode.json"
    matches = [name for name, entry in metadata["configs"].items() if entry["model_id"] == model_id]
    if matches != [relative]:
        raise WorkspaceError("NVIDIA registered profile mapping is missing or ambiguous.")
    return relative


def read_catalog(path=SNAPSHOT):
    data = read_regular_file(path)
    models = parse_catalog(data)
    for model_id in PRIMARY:
        canonical_candidate(models, model_id)
    return models, hashlib.sha256(data).hexdigest()
