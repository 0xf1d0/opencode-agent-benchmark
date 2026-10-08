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

## Canonical Aristote catalog

The owner personally authenticated and supplied the exact
[Aristote snapshot](aristote/catalog-snapshots/2026-10-08.json) from
`GET https://llm.aristote.education/v1/models`, dated 2026-10-08. SHA-256:
`ace8258a30778b5a7eaef0ce22e20bbe2c95c15ba1c4c9b495b7589586312e69`.
It establishes owner-account catalog membership at that date, not successful
OpenCode inference or tools. The exact snapshot supersedes historical documentation
for membership; its bytes are unchanged. No aliases are supplied or invented.

| Canonical ID | Classification | Active restricted profile |
| --- | --- | --- |
| `qwen-3.6-35b-instruct` | First preflight / priority | Yes |
| `qwen-3.6-35b-instruct-reasoning-high` | Separate served condition / priority | Yes |
| `qwen-3.8-27b` | Additional priority | Yes |
| `mistral-small-3.2-24b` | Family comparison priority | Yes |
| `mistral-small-4-119b` | Priority candidate; capabilities unknown | Yes |
| `gemma-4-31b` | Optional secondary | No |
| `llama-3.1-8b` | Optional secondary | No |
| `mistral-medium-latest` | floating_alias; immutable underlying model unknown | No |
| `bge-m3` | Excluded: catalog mode embedding | No |
| `bge-reranker-v2-m3` | Excluded: catalog mode rerank | No |

Each priority cell has one `<canonical-id>/opencode.json`; the former single root
Aristote config is removed. Workspace creation and runtime locks use exact IDs,
verify the snapshot hash against metadata, reject unknown/floating/excluded IDs,
and retain the catalog hash outside the agent workspace. No ID normalization or
alias resolution occurs. Missing `mode` remains null: candidate classification is
an explicit reviewed selection policy, not evidence of chat/tool capability.

Metadata preserves each full `api_record_raw`, `api_owned_by_raw`, `api_created_raw`
and `api_mode_raw`. The repeated `owned_by: openai` does **not** establish OpenAI
ownership; `upstream_model_ownership` remains null. The repeated creation value is
not treated as a release date: `created_semantics_verified: false` and
`upstream_release_date: null`. Absent aliases are null, not a fabricated alias list.
Conversational service context/output limits, checkpoint/weight revision,
quantization, tokenizer, decoding, tools, performance and actual prices are null.
Embedding-specific raw token fields are preserved without applying them to LLMs.

The 32768 context / 4096 output caps are
`benchmark_extension_provisional_common_cap`, never Aristote service ceilings.
Reasoning-high is a distinct condition even though it shares a family label with
standard Qwen; reasoning effort and implementation remain unverified.
`mistral-medium-latest` needs independent immutable served-version evidence before
controlled eligibility and is not asserted equivalent to direct `mistral-medium-3-5`.

Albert `mistral-small-3-2-24b-instruct-2506` versus Aristote
`mistral-small-3.2-24b` is **model-family-only**. Keep this possible provider
comparison, without claiming identical checkpoints, quantization or settings.

## Other providers

- NVIDIA retains `z-ai/glm-5.3`, published by [NVIDIA Build](https://build.nvidia.com/z-ai/glm-5-3?section=deploy).
- Mistral retains `zai-glm-5-3`, published by [Mistral](https://docs.mistral.ai/models/zai-glm-5-3),
  and `mistral-medium-3-5` in `opencode.medium.json`, documented on its
  [Medium card](https://docs.mistral.ai/models/mistral-medium-3-5-26-04).

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
python scripts/create_workspace.py --benchmark toy --provider aristote \
  --model qwen-3.6-35b-instruct --run-id aristote-preflight-001
```

Mistral Medium requires `--config providers/mistral/opencode.medium.json` and
`--model mistral-medium-3-5`. Default Mistral is `zai-glm-5-3`. Default Aristote is
`qwen-3.6-35b-instruct`. Preparing a workspace establishes no runtime readiness.

[Preflight representation](../docs/preflight.md) separates configuration loading,
provider/model appearance, inference, conversation, tool calling, permissions,
context/output acceptance and routing. Aristote checks remain unperformed. The
owner reports Albert Qwen3 Coder basic inference and file editing succeeded in the
restricted condition; dates, runtime pins and sanitized evidence are not yet
recorded, so this is a separate owner observation, not a completed formal record.
The blank Albert template remains unperformed; no checks were marked passed by
Codex. Both providers remain `scored_ready: false`. Catalog qualification
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
