"""Offline Mistral catalog/alias-card evidence; never authenticate or infer weights."""

import hashlib
from pathlib import Path
import re

if __package__:
    from scripts.create_workspace import WorkspaceError, load_json, read_regular_file
else:
    from create_workspace import WorkspaceError, load_json, read_regular_file


SNAPSHOT = Path(__file__).resolve().parents[1] / "providers/mistral/catalog-snapshots/2026-10-08.json"
PRIMARY = ("mistral-medium-3-5", "mistral-small-2603", "codestral-2508")
OPTIONAL = ("ministral-14b-2512", "ministral-8b-2512", "ministral-3b-2512", "labs-leanstral-1-5-1")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,255}")
CARD_FIELDS = (
    "name", "billing_model_name", "capabilities", "max_context_length", "type",
    "description", "deprecation", "deprecation_replacement_model", "default_model_temperature",
)


def parse_catalog(data):
    catalog = load_json(data)
    if not isinstance(catalog, dict) or catalog.get("object") != "list" or not isinstance(catalog.get("data"), list):
        raise WorkspaceError("Mistral catalog must be object=list with a data array.")
    models = {}
    for entry in catalog["data"]:
        if not isinstance(entry, dict):
            raise WorkspaceError("Mistral model records must be objects.")
        model_id = entry.get("id")
        if not isinstance(model_id, str) or not IDENTIFIER.fullmatch(model_id) or model_id in models:
            raise WorkspaceError("Invalid or duplicate exact Mistral catalog ID.")
        if entry.get("object") != "model":
            raise WorkspaceError("Invalid Mistral model object type.")
        capabilities = entry.get("capabilities")
        if not isinstance(capabilities, dict) or any(type(value) is not bool for value in capabilities.values()):
            raise WorkspaceError("Mistral capabilities must be a boolean-valued object.")
        aliases = entry.get("aliases")
        if not isinstance(aliases, list) or any(not isinstance(alias, str) or not IDENTIFIER.fullmatch(alias) for alias in aliases):
            raise WorkspaceError("Invalid Mistral aliases.")
        if len(set(aliases)) != len(aliases) or model_id in aliases:
            raise WorkspaceError("Duplicate or self-referencing Mistral alias.")
        context = entry.get("max_context_length")
        if context is not None and (type(context) is not int or context <= 0):
            raise WorkspaceError("Invalid declared Mistral context length.")
        models[model_id] = entry
    # An alias may also be an ID. Validate linked cards instead of rejecting that
    # expected API structure or identifying weights from a shared billing name.
    alias_clusters(models)
    return models


def alias_clusters(models):
    adjacency = {model_id: set() for model_id in models}
    for model_id, entry in models.items():
        for alias in entry["aliases"]:
            if alias not in models:
                continue
            peer = models[alias]
            if model_id not in peer["aliases"]:
                raise WorkspaceError("Returned Mistral alias links are not reciprocal; human review required.")
            for field in CARD_FIELDS:
                if field in entry and field in peer and entry[field] != peer[field]:
                    raise WorkspaceError("Linked Mistral cards have conflicting shared fields; human review required.")
            adjacency[model_id].add(alias)
            adjacency[alias].add(model_id)
    remaining = set(models)
    clusters = []
    while remaining:
        pending = [min(remaining)]
        members = set()
        while pending:
            model_id = pending.pop()
            if model_id not in members:
                members.add(model_id)
                pending.extend(adjacency[model_id] - members)
        remaining -= members
        preferred = next((model_id for model_id in PRIMARY + OPTIONAL if model_id in members), None)
        ordered = sorted(members)
        first = models[ordered[0]]
        clusters.append({
            "cluster_id": "card-" + hashlib.sha256("\n".join(ordered).encode()).hexdigest()[:16],
            "catalog_ids": ordered,
            "preferred_benchmark_id": preferred,
            "floating_catalog_ids": [model_id for model_id in ordered if model_id.endswith("-latest")],
            "external_aliases_not_returned": sorted(set().union(*(set(models[model_id]["aliases"]) for model_id in ordered)) - set(models)),
            "apparent_shared_model_card": {field: first.get(field) for field in CARD_FIELDS},
            "identity_basis": "reciprocal_catalog_alias_links_and_consistent_shared_card_fields",
            "exact_served_checkpoint_identity": None,
            "served_checkpoint_equivalence_verified": False,
        })
    return clusters


def candidate_status(entry):
    capabilities = entry["capabilities"]
    if capabilities.get("completion_chat") is False:
        advertised = [key for key in ("ocr", "moderation", "classification", "audio_transcription", "audio_transcription_realtime", "audio_speech") if capabilities.get(key) is True]
        return "excluded", "completion_chat=false; " + ("advertised service capabilities: " + ", ".join(advertised) if advertised else "no general conversational coding interface advertised") + "."
    if capabilities.get("completion_chat") is not True or capabilities.get("function_calling") is not True:
        return "unreviewed", "Chat and function-calling capability declarations are required for candidate selection."
    if capabilities.get("audio") is True:
        return "not_initial_audio_chat", "Audio-chat capability is preserved but outside the initial general coding matrix."
    if entry["id"].endswith("-latest"):
        return "floating_alias", "Floating catalog ID; select the reviewed preferred stable ID instead."
    if entry["id"] in PRIMARY:
        return "priority", None
    if entry["id"] in OPTIONAL:
        return "optional", "Lean/formal-proof specialization; not a general initial coding candidate." if entry["id"] == "labs-leanstral-1-5-1" else None
    return "not_selected", "Returned alias/card ID is not a preferred benchmark cell; no automatic alias expansion."


def canonical_candidate(models, model_id):
    if model_id not in models:
        raise WorkspaceError("Mistral model must be an exact returned preferred catalog ID.")
    if candidate_status(models[model_id])[0] not in {"priority", "optional"}:
        raise WorkspaceError("Mistral ID is floating, excluded or not a preferred benchmark candidate.")
    return models[model_id]


def read_catalog(path=SNAPSHOT):
    data = read_regular_file(path)
    models = parse_catalog(data)
    for model_id in PRIMARY:
        canonical_candidate(models, model_id)
    return models, hashlib.sha256(data).hexdigest()
