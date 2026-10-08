# NVIDIA Build catalog and profile review

## Exact owner evidence

The repository owner authenticated `GET https://integrate.api.nvidia.com/v1/models`
and reported HTTP 200 on 2026-10-08. No request was made by Codex. The exact stored
sanitized [snapshot](../providers/nvidia/catalog-snapshots/2026-10-08.json) contains
**80** unique records. Its SHA-256 is:

`2e7d19e2a7d4d8602a2b039de78b4af3e8b45920d34f50393947e53457d6849d`

The offline parser requires strict UTF-8 JSON, `object=list`, a data array,
object records, unique exact namespaced IDs, `object=model`, integer raw `created`
and string raw `owned_by`. It preserves additional fields without requiring
undocumented capabilities. All records are preserved in metadata. There are no
catalog aliases; metadata aliases stay null. Raw `created=735790403` is not a
release timestamp; raw `owned_by` is not deployment/operator proof.

## Active primary cells and safe paths

| Exact canonical API model ID | Directory under `providers/nvidia/` |
| --- | --- |
| `nvidia/nemotron-3-ultra-550b-a55b` | `nvidia-nemotron-3-ultra-550b-a55b` |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | `nvidia-nemotron-3.5-lightning-30b-a3b` |
| `z-ai/glm-5.3` | `z-ai-glm-5.3` |

Each directory has one restricted `opencode.json`, with only that model/provider
enabled. The OpenCode selector prepends provider ID `nvidia` to the full API ID;
`nvidia/nvidia/nemotron-3.5-lightning-30b-a3b` is intentional. An explicit registry
is validated before paths are resolved; raw model IDs never become filesystem
paths. Unknown, excluded, optional, comparison-only and renamed IDs fail closed,
even with an override. Registered config-byte drift also fails closed. Initial
metadata records the snapshot SHA-256 outside the workspace; agent contents are
only fixture code, public test, selected config and isolated Git baseline.

The previous root `providers/nvidia/opencode.json` was migrated to
`z-ai-glm-5.3/opencode.json`; historical exact SHA-256
`859dfc2485a0c475d966684b035e1d9669969cc51748177c1cc3533b01ff4149`
is retained in metadata. No active root profile remains. Local context 32768 and
output 4096 are `benchmark_extension_provisional_common_cap`, not service ceilings.
Shell/web/external-directory access remains denied, sharing/autoupdate disabled.

## Separate public evidence

The hashed [dated fact record](../providers/nvidia/evidence/2026-10-08-public-model-cards.json)
is an authored summary of public pages, not a copied API response or full webpage
archive. [Ultra's card](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b/modelcard)
advertises reasoning, code and tool workflows;
[Lightning's card](https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b/modelcard)
targets long-running agents. [GLM's card](https://build.nvidia.com/z-ai/glm-5-3/modelcard)
advertises reasoning/tool use and explicitly claims an NVFP4 hosted endpoint
using vLLM/Dynamo. These are public claims, independent of the sparse catalog and
not observed inference results. No relative superiority or hosted/downloaded
weight equivalence is inferred. No conflicting value was found for fields
compared during this review; absent catalog fields are not disagreements.

## Optional reviewed candidates (no active profiles)

- `nvidia/nemotron-3-super-120b-a12b`
- `deepseek-ai/deepseek-v4.1-flash`
- `moonshotai/kimi-k3`
- `moonshotai/kimi-k2.6`
- `poolside/laguna-xs-2.1`

## Specialized service exclusions

These 18 exact IDs are excluded by explicit reviewed identifier evidence, not
invented capability fields or a blanket name filter. Public
[Nemotron Parse documentation](https://build.nvidia.com/nvidia/nemotron-parse/modelcard)
also supports document-extraction specialization. Other exclusions here retain
ID-based evidence only; no unavailable public card content is claimed verified.

| Canonical ID | Exclusion reason |
| --- | --- |
| `meta/llama-guard-4-12b` | Explicit guard/safety/topic-control service identifier; not a general coding cell. |
| `nvidia/ai-synthetic-video-detector` | Explicit synthetic-video detection identifier; outside coding tasks. |
| `nvidia/embed-qa-4` | Explicit embedding/retrieval service identifier; not a conversational coding cell. |
| `nvidia/llama-3.1-nemoguard-8b-content-safety` | Explicit guard/safety/topic-control service identifier; not a general coding cell. |
| `nvidia/llama-3.1-nemoguard-8b-topic-control` | Explicit guard/safety/topic-control service identifier; not a general coding cell. |
| `nvidia/llama-3.1-nemotron-safety-guard-8b-v3` | Explicit guard/safety/topic-control service identifier; not a general coding cell. |
| `nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1` | Explicit embedding/retrieval service identifier; not a conversational coding cell. |
| `nvidia/llama-3.2-nv-embedqa-1b-v1` | Explicit embedding/retrieval service identifier; not a conversational coding cell. |
| `nvidia/llama-nemotron-embed-vl-1b-v2` | Explicit embedding/retrieval service identifier; not a conversational coding cell. |
| `nvidia/nemotron-3-embed-1b` | Explicit embedding/retrieval service identifier; not a conversational coding cell. |
| `nvidia/nemotron-3.5-content-safety` | Explicit guard/safety/topic-control service identifier; not a general coding cell. |
| `nvidia/nemotron-4-340b-reward` | Explicit reward-model identifier; not a conversational coding cell. |
| `nvidia/nemotron-parse` | Explicit parsing service identifier; outside the general coding matrix. |
| `nvidia/nemotron-parse-2.0` | Explicit parsing service identifier; outside the general coding matrix. |
| `nvidia/nv-embedqa-mistral-7b-v2` | Explicit embedding/retrieval service identifier; not a conversational coding cell. |
| `nvidia/riva-translate-4b-instruct` | Explicit translation service identifier; outside the general coding matrix. |
| `nvidia/riva-translate-4b-instruct-v2` | Explicit translation service identifier; outside the general coding matrix. |
| `snowflake/arctic-embed-l` | Explicit embedding/retrieval service identifier; not a conversational coding cell. |

## Unreviewed catalog records

These 53 entries are preserved but not enabled or automatically excluded as
unsuitable. Their sparse records alone do not establish conversational/tool
capabilities. Explicit candidate review and an active profile would be needed.

- `01-ai/yi-large`
- `adept/fuyu-8b`
- `ai21labs/jamba-1.5-large-instruct`
- `aisingapore/sea-lion-7b-instruct`
- `bigcode/starcoder2-15b`
- `databricks/dbrx-instruct`
- `deepseek-ai/deepseek-coder-6.7b-instruct`
- `google/codegemma-1.1-7b`
- `google/codegemma-7b`
- `google/deplot`
- `google/diffusiongemma-26b-a4b-it`
- `google/gemma-2b`
- `google/gemma-3-12b-it`
- `google/gemma-3-4b-it`
- `google/recurrentgemma-2b`
- `ibm/granite-3.0-3b-a800m-instruct`
- `ibm/granite-3.0-8b-instruct`
- `ibm/granite-34b-code-instruct`
- `ibm/granite-8b-code-instruct`
- `meta/codellama-70b`
- `meta/llama-3.2-11b-vision-instruct`
- `meta/llama-3.2-90b-vision-instruct`
- `meta/llama2-70b`
- `meta/muse-glimmer-30b`
- `microsoft/kosmos-2`
- `microsoft/phi-3-vision-128k-instruct`
- `microsoft/phi-3.5-moe-instruct`
- `mistralai/codestral-22b-instruct-v0.1`
- `mistralai/mistral-7b-instruct-v0.3`
- `mistralai/mistral-large`
- `mistralai/mistral-large-2-instruct`
- `mistralai/mixtral-8x22b-v0.1`
- `nv-mistralai/mistral-nemo-12b-instruct`
- `nvidia/cosmos-reason2-8b`
- `nvidia/ising-calibration-1.5-31b`
- `nvidia/llama-3.1-nemotron-51b-instruct`
- `nvidia/llama-3.1-nemotron-70b-instruct`
- `nvidia/llama-3.1-nemotron-ultra-253b-v1`
- `nvidia/llama3-chatqa-1.5-70b`
- `nvidia/mistral-nemo-minitron-8b-8k-instruct`
- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`
- `nvidia/nemotron-4-340b-instruct`
- `nvidia/nemotron-nano-3-30b-a3b`
- `nvidia/neva-22b`
- `nvidia/nvclip`
- `nvidia/vila`
- `openai/gpt-oss-20b`
- `writer/palmyra-creative-122b`
- `writer/palmyra-fin-70b-32k`
- `writer/palmyra-med-70b`
- `writer/palmyra-med-70b-32k`
- `z-ai/glm-5.3-flash`
- `zyphra/zamba2-7b-instruct`

## Cross-provider evidence and unknowns

`google/gemma-4-31b-it` is comparison-only (no profile), paired with Albert's
`gemma-4-31b-it` and recorded alias `google/gemma-4-31B-it`. This is
**model-family-only**: checkpoint, quantization and serving identity are unverified.
NVIDIA `openai/gpt-oss-20b` versus Albert `gpt-oss-120b` are different sizes, not a
same-model provider comparison. NVIDIA `deepseek-ai/deepseek-v4.1-flash` versus
Albert `deepseek-v4-flash-0731` have related family labels but differing versions;
no identical checkpoint is asserted. The former direct-Mistral `zai-glm-5-3` is
absent from its current owner catalog; no NVIDIA/Mistral GLM pair is executable.

Catalog capability/context/output/pricing/modality fields stay null, as do
observed checkpoint/revision, hosted quantization, tokenizer, decoding, tool
compatibility, latency and throughput. Public model-card claims remain separate.
Operator/deployment/retention/certification evidence remains unknown in the
sovereignty card; ownership labels do not supply it. Credential storage stays
null/unverified and is never inspected. OpenCode runtime version and successful
credential usability are unobserved/null in repository evidence.

## Qualification and deterministic validation

All four providers have authenticated catalog evidence. Albert/Aristote basic
owner observations are separate from formal qualification. NVIDIA and Mistral
formal preflights are unperformed; no provider/model cell is scored-ready.
[Lightning manual steps](preflight-nvidia.md) and the
[unperformed template](../runtime/preflight.nvidia.example.json) are ready for the
owner. All nine checks remain `not_run`, observations null, `scored_ready=false`.
Do not link a task-prompt runtime lock to this non-task smoke session.

Infrastructure checks cover strict parsing, raw preservation/nulls, classifications,
exact snapshot/config/evidence hashes, registry ambiguity/traversal, canonical
slash-ID CLI selection, override rejection, workspace allowlists/baselines,
runtime-lock provenance and blank preflight status. Local validation: **78 infrastructure tests passed**, including all **15 active
provider profiles**; `git diff --check` and local Markdown-link checks passed.
GitHub CI was not executed in this session. CI discovers the same tests
without credentials or OpenCode. The intentional public baseline remains two
passes and one named palindrome failure; no oracle or benchmark solution runs.

Before formal preflight: select/pin a real OpenCode release, retain dated sanitized
probe evidence, audit effective settings/routing and review the isolation design.
Before scoring: implement/audit the reviewed runtime, complete all formal checks,
freeze the campaign protocol, and finish external collection/evaluation and human
review gates. This phase implements no sandbox, agentic runtime or scored runner.
