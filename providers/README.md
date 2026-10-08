# Provider profiles and evidence

The fixed provider IDs are `nvidia`, `mistral`, `albert`, `aristote`. All active
configs are secret-free OpenCode v1 JSON, with updates disabled. Their current
track is **restricted**: read/search/edit are enabled; shell, web, delegation,
plugins, MCP, LSP and formatters are disabled. These permissions are not an OS
firewall. No profile is `scored_ready`; no authenticated calls were made by Codex.

## Authentication boundary

Authentication mode is `opencode_managed_persistent_credential`. All active configs
omit `apiKey` and authentication headers, preserving the owner's `/connect` state.
The owner observed that custom `albert`/`aristote` definitions must be loaded from
the project for `/connect` and model selection to recognize them. Run preparation
preserves those exact IDs. Credential storage location is null and unverified;
its backend is irrelevant. Never inspect account storage, auth files, databases,
key-bearing environment values or any other credential source. Credential
presence/usability is null until a separate owner-driven preflight establishes it.
No benchmark code discovers storage locations or copies credentials. A future
runtime must keep authentication outside model-controlled commands.

## Canonical Albert catalog

The owner personally authenticated and supplied
[`catalog-snapshots/2026-10-08.json`](albert/catalog-snapshots/2026-10-08.json)
from `GET https://albert.api.etalab.gouv.fr/v1/models`.
The exact sanitized snapshot SHA-256 is
`0fc3ed2b2fc5c581a1d175cd6a98cb9b64c85bb850431eb1990650f5c5ab1e0e`.
Its retrieval date is 2026-10-08; exact time is null. It proves account-specific
catalog membership at that date, not successful inference, tool calling or public
access. No historical search excerpt overrides it. Snapshot bytes are preserved.

| Canonical `id` | Priority | Declared context |
| --- | --- | ---: |
| `qwen3-coder-30b-a3b-instruct` | First preflight / primary | 262144 |
| `gpt-oss-120b` | Initial candidate | 131072 |
| `deepseek-v4-flash-0731` | Initial candidate | 131072 |
| `mistral-small-3-2-24b-instruct-2506` | Initial candidate | 128000 |
| `ministral-3-8b-instruct-2512` | Optional; no active config | 262144 |
| `gemma-4-31b-it` | Optional; no active config | 262144 |

Each initial candidate has exactly one `<canonical-id>/opencode.json`. The workspace
generator selects it by exact `--model`. Aliases such as `openweight-code` and
`deepseek-v4-flash` are provenance only and are rejected as run model IDs.
`Mistral-Medium-3.5-128B` is absent and retired; its former active configs were
removed. Do not claim Albert currently serves Mistral Medium 3.5.

The raw snapshot retains `bge-m3`, `bge-reranker-v2-m3`, `qwen3-vl-embedding-8b`,
`whisper-large-v3`, `lightonocr-2-1b`. They are excluded respectively as embedding,
reranking, embedding, ASR and OCR models. Image-text typing alone does not qualify
OCR for coding. The offline parser validates structure; unreviewed new IDs are not
automatically promoted. Metadata preserves aliases, types, `owned_by`, context and
advertised prompt/completion costs. Catalog costs are 0.0; unit, currency and actual
billing are unknown. Context declarations are not output ceilings.

## Other providers

- NVIDIA retains `z-ai/glm-5.3`, published by [NVIDIA Build](https://build.nvidia.com/z-ai/glm-5-3?section=deploy).
- Mistral retains `zai-glm-5-3`, published by [Mistral](https://docs.mistral.ai/models/zai-glm-5-3),
  and `mistral-medium-3-5` in `opencode.medium.json`, documented on its
  [Medium card](https://docs.mistral.ai/models/mistral-medium-3-5-26-04).
- Aristote retains `qwen-3.6-35b-instruct` from the owner's supplied **Détails
  techniques** text, independent of the historical TP. Exact page URL/publication
  date and current account catalog remain unknown. Owner catalog and runtime
  qualification are required before scoring.

The NVIDIA/Mistral GLM comparison is **same-model-family**, not established
identical weights. Mistral Medium direct remains useful independently of Albert.
Aristote is not Albert. All served revisions, quantization, decoding and tool
reliability remain null unless separately evidenced. Documentation was reviewed
on 2026-10-07; this change does not refresh hosted availability.

## Preparation and qualification

```sh
python scripts/create_workspace.py --benchmark toy --provider albert \
  --model qwen3-coder-30b-a3b-instruct --run-id preparation-001
python scripts/create_workspace.py --benchmark toy --provider nvidia \
  --model z-ai/glm-5.3 --run-id preparation-001
```

Mistral Medium requires `--config providers/mistral/opencode.medium.json` and
`--model mistral-medium-3-5`. Default Mistral is `zai-glm-5-3`. Default Aristote is
`qwen-3.6-35b-instruct`. Preparing a workspace establishes no runtime readiness.

[Preflight representation](../docs/preflight.md) separates configuration loading,
provider/model appearance, inference, conversation, tool calling, permissions,
context/output acceptance and routing. All are unperformed. Catalog qualification
alone is not `scored_ready`. Unknown measurements are null, never inferred from a
connected icon. Current local 32768/4096 caps are provisional benchmark choices,
not service maxima; Aristote's documentation applied those local caps to specific
Reasoning High/Mistral configurations, not all models.

Restricted agents cannot launch pytest/Git through shell; an external harness is
required and remains unimplemented. Before scoring, isolate merged OpenCode
configuration, inspect effective secret-free settings, pin the release and verify
egress and permission behavior. [Runtime design](../docs/runtime.md) separates
inference transport from model-controlled commands. Metadata also keeps deployment,
hosting, verified certification and retention evidence separate from capability.
