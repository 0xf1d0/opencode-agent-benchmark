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

## Mistral AI direct owner catalog

The exact [owner-authenticated Mistral snapshot](mistral/catalog-snapshots/2026-10-08.json)
from `GET https://api.mistral.ai/v1/models`, retrieved on 2026-10-08, contains
**46 returned records**. SHA-256:
`4246145d5629c7106aaefe4e0831cd4d9e9178e868f3c3b9c5feaced36178373`.
Its bytes are unchanged. Unlike Albert, aliases may also be returned `id` records.
The validator builds 17 alias-linked groups using reciprocal links and consistent
shared card fields. Equal billing names alone do not merge cards. These groups
establish apparent card relationships, not identical served checkpoints.

| Preferred initial ID | Catalog context | Advertised capabilities |
| --- | ---: | --- |
| `mistral-medium-3-5` | 262144 | Chat, function calling, reasoning, vision |
| `mistral-small-2603` | 262144 | Chat, function calling, reasoning, vision |
| `codestral-2508` | 256000 | Chat, function calling, FIM; reasoning false |

Each has one `<preferred-id>/opencode.json`. Medium is the default general candidate;
Codestral is the coding-specialized candidate. Catalog capabilities are declarations,
not evidence of successful OpenCode tool calls. Optional fixed IDs are
`ministral-14b-2512`, `ministral-8b-2512`, `ministral-3b-2512`, and specialized
Lean/formal-proof `labs-leanstral-1-5-1`; none has an initial config.

The primary clusters preserve these additional returned IDs as provenance only:

- Medium: `mistral-medium-latest`, `mistral-medium`, `mistral-medium-3.5`,
  `mistral-medium-3`, `mistral-medium-2604`, `mistral-vibe-cli-latest`,
  `mistral-vibe-cli-with-tools`, `magistral-medium-latest`.
- Small 4: `mistral-small-latest`, `mistral-vibe-cli-fast`, `magistral-small-latest`.
- Codestral: `codestral-latest`, `mistral-code-latest`, `mistral-code-fim-latest`.

All `*-latest` IDs are flagged floating. Non-preferred aliases are also rejected
as benchmark cells, even if their strings appear dated. No implicit alias resolution
or duplicate cell per returned card. Full clusters, raw records and exclusions are
in `mistral/metadata.json`; see [the review inventory](../docs/mistral-review.md).

Nineteen records advertise `completion_chat: false` and are excluded, including
embedding-named records, moderation, OCR, transcription/realtime and speech services.
Specific capability flags justify the specialized service descriptions. Embedding
records advertise no embedding-specific flag, so their coding exclusion relies on
`completion_chat: false`, not an invented embedding capability. Two audio-chat
records remain provenance outside the initial general coding matrix. Every original
field, alias list and capability object is retained; raw creation timestamps do not
become upstream release dates. Served revision, quantization, tokenizer, decoding,
output ceilings, actual prices and runtime performance remain null.

Public [Mistral Small 4 documentation](https://docs.mistral.ai/models/mistral-small-4-0-26-03)
identifies `mistral-small-2603` as 119B total / 6.5B active. Its Aristote pairing
`mistral-small-4-119b` is **model-family-only**, not a serving-equivalence claim.
The [Medium card](https://docs.mistral.ai/models/mistral-medium-3-5-26-04)
supports the selected preferred spelling. The
[Codestral card](https://docs.mistral.ai/models/codestral-25-08) says **128k** context,
conflicting with the authenticated catalog's **256000**. Both are recorded in dated
[public evidence](mistral/evidence/2026-10-08-public-model-cards.json); the conflict
is unresolved, and no exact numerical expansion of `k` is guessed. The evidence
file hashes authored observations, not remote HTML bytes. Local 32768/4096 caps
remain `benchmark_extension_provisional_common_cap`, independent of service maxima.

`zai-glm-5-3` is absent from this owner catalog. Its former root config is retired;
NVIDIA/Mistral GLM 5.3 is historical/planned, **not currently executable** for this
account. NVIDIA retains `z-ai/glm-5.3` ([Build evidence](https://build.nvidia.com/z-ai/glm-5-3?section=deploy)).
The direct account has no fixed Small 3.2 ID: do not fabricate a three-provider
Small 3.2 comparison. `opencode.medium.json` moved into the Medium directory with
identical bytes and recorded migration hashes.

## Preparation and qualification

```sh
python scripts/create_workspace.py --benchmark toy --provider albert \
  --model qwen3-coder-30b-a3b-instruct --run-id preparation-001
python scripts/create_workspace.py --benchmark toy --provider nvidia \
  --model nvidia/nemotron-3.5-lightning-30b-a3b --run-id nvidia-lightning-preflight-001
python scripts/create_workspace.py --benchmark toy --provider aristote \
  --model qwen-3.6-35b-instruct --run-id aristote-preflight-001
```

Mistral automatically resolves `mistral-medium-3-5`, `mistral-small-2603` and
`codestral-2508` into their model directories. Its default candidate is Medium.
Unknown, floating, excluded and non-preferred returned IDs fail closed, even with
an explicit config override. Default Aristote is
`qwen-3.6-35b-instruct`. Preparing a workspace establishes no runtime readiness.

[Preflight representation](../docs/preflight.md) separates configuration loading,
provider/model appearance, inference, conversation, tool calling, permissions,
context/output acceptance and routing. Mistral's template is unperformed. The
owner reports Aristote standard Qwen basic loading, trivial inference and file
creation worked, while a `pwd` request used permitted file/search tools without
shell execution/stdout. This is a basic restricted observation, not complete
permission/routing proof. The
owner reports Albert Qwen3 Coder basic inference and file editing succeeded in the
restricted condition; dates, runtime pins and sanitized evidence are not yet
recorded, so this is a separate owner observation, not a completed formal record.
The blank formal templates remain unperformed; no checks were marked passed by
Codex. All providers remain `scored_ready: false`. Catalog qualification
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


For the first owner-only Mistral restricted smoke observation, use the
[exact manual steps](../docs/preflight-mistral.md). This is not a scored campaign
or a substitute for the reviewed OS boundary and complete formal qualification.


## NVIDIA Build owner catalog

All four providers now have dated owner-authenticated catalogs. The exact
[NVIDIA snapshot](nvidia/catalog-snapshots/2026-10-08.json) has 80 records, HTTP
200 reported by the owner, and SHA-256
`2e7d19e2a7d4d8602a2b039de78b4af3e8b45920d34f50393947e53457d6849d`.
Only sparse raw fields are present. `created=735790403` has unverified semantics;
`owned_by` is not operator/hosting evidence. Aliases and absent service metadata
remain null. [Public card facts](nvidia/evidence/2026-10-08-public-model-cards.json)
are separate hashed evidence, not additional authenticated API fields.

| Canonical API ID | Registered directory | Role |
| --- | --- | --- |
| `nvidia/nemotron-3-ultra-550b-a55b` | `nvidia-nemotron-3-ultra-550b-a55b` | Primary |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | `nvidia-nemotron-3.5-lightning-30b-a3b` | Primary; first manual preflight |
| `z-ai/glm-5.3` | `z-ai-glm-5.3` | Primary |

Each directory contains exactly one selected-model `opencode.json`. OpenCode's
model selector is `<provider>/<canonical API ID>`, e.g.
`nvidia/nvidia/nemotron-3.5-lightning-30b-a3b`; preserve both namespaces. The old
root GLM profile is migrated with its previous hash recorded. Preparation uses
explicit mappings, rejects unknown/non-selected IDs and config drift, and records
the catalog hash outside the workspace. Authentication remains opaque external
OpenCode-managed state under provider ID `nvidia`; no key mechanism is added.
All profiles retain restricted tool policy and provisional benchmark caps.

Five optional candidates, 18 specialized exclusions and 53 unreviewed entries
are listed in the [complete review](../docs/nvidia-review.md). NVIDIA/Albert Gemma
4 31B is a future **model-family-only** candidate. GPT OSS 20B/120B and differing
DeepSeek labels are not identical-model pairs. Direct-Mistral GLM remains absent.
No NVIDIA runtime checks have run. Follow the [owner Lightning protocol](../docs/preflight-nvidia.md);
the [blank template](../runtime/preflight.nvidia.example.json) stays entirely
`not_run`/null/false. Catalog-qualified does not mean formally preflight-qualified
or scored-ready; no cell is scored-ready.
