# Mistral catalog review — 2026-10-08

The exact owner-authenticated snapshot contains **46 records**. SHA-256:
`4246145d5629c7106aaefe4e0831cd4d9e9178e868f3c3b9c5feaced36178373`. The source is `GET https://api.mistral.ai/v1/models`; retrieval time is null. No provider requests or credential inspection were performed by Codex.

## Preferred cells and migration

Active restricted configurations are `mistral-medium-3-5/opencode.json`, `mistral-small-2603/opencode.json`, `codestral-2508/opencode.json` under `providers/mistral/`. The former GLM root config is retired because `zai-glm-5-3` is absent. The old Medium file migrated byte-for-byte; before/after hashes are retained in metadata. No other returned alias creates a benchmark cell.

## Apparent alias-card groups

The validator finds **17 groups**. Each row lists exact returned IDs linked by reciprocal aliases with consistent shared fields. Neither common billing names nor shared card fields prove identical served checkpoints. The two OCR 4 rows remain separate despite sharing a billing name.

| Preferred benchmark ID | Returned IDs in group |
| --- | --- |
| `codestral-2508` | `codestral-2508`, `codestral-latest`, `mistral-code-fim-latest`, `mistral-code-latest` |
| None selected | `codestral-embed`, `codestral-embed-2505` |
| `labs-leanstral-1-5-1` | `labs-leanstral-1-5`, `labs-leanstral-1-5-1` |
| `mistral-medium-3-5` | `magistral-medium-latest`, `mistral-medium`, `mistral-medium-2604`, `mistral-medium-3`, `mistral-medium-3-5`, `mistral-medium-3.5`, `mistral-medium-latest`, `mistral-vibe-cli-latest`, `mistral-vibe-cli-with-tools` |
| `mistral-small-2603` | `magistral-small-latest`, `mistral-small-2603`, `mistral-small-latest`, `mistral-vibe-cli-fast` |
| `ministral-14b-2512` | `ministral-14b-2512`, `ministral-14b-latest` |
| `ministral-3b-2512` | `ministral-3b-2512`, `ministral-3b-latest` |
| `ministral-8b-2512` | `ministral-8b-2512`, `ministral-8b-latest` |
| None selected | `mistral-embed`, `mistral-embed-2312` |
| None selected | `mistral-moderation-2603` |
| None selected | `mistral-ocr-2512`, `mistral-ocr-3`, `mistral-ocr-3-0` |
| None selected | `mistral-ocr-4`, `mistral-ocr-4-1`, `mistral-ocr-latest` |
| None selected | `mistral-ocr-4-0` |
| None selected | `voxtral-mini-2602`, `voxtral-mini-latest` |
| None selected | `voxtral-mini-realtime-2602`, `voxtral-mini-realtime-latest`, `voxtral-mini-transcribe-realtime-2602` |
| None selected | `voxtral-mini-tts-2603`, `voxtral-mini-tts-latest` |
| None selected | `voxtral-small-2507`, `voxtral-small-latest` |

## Floating IDs

All 16 `*-latest` returned IDs are flagged floating independently of their service exclusion status. Other non-preferred aliases also fail closed.

`codestral-latest`, `mistral-code-latest`, `mistral-code-fim-latest`, `ministral-14b-latest`, `ministral-3b-latest`, `ministral-8b-latest`, `mistral-medium-latest`, `mistral-vibe-cli-latest`, `magistral-medium-latest`, `mistral-small-latest`, `magistral-small-latest`, `voxtral-small-latest`, `mistral-ocr-latest`, `voxtral-mini-latest`, `voxtral-mini-realtime-latest`, `voxtral-mini-tts-latest`.

## Optional and excluded records

Optional, unconfigured fixed candidates: `ministral-14b-2512`, `ministral-8b-2512`, `ministral-3b-2512`, `labs-leanstral-1-5-1`. Leanstral is specialized for Lean/formal proof rather than the initial general coding matrix.

All 19 records below advertise `completion_chat: false`. Additional true capability flags identify specialized services; the embedding-named records lack a dedicated embedding flag, so no such flag is invented.

| Excluded returned ID | Capability evidence |
| --- | --- |
| `codestral-embed` | completion_chat=false; no general conversational coding interface advertised. |
| `codestral-embed-2505` | completion_chat=false; no general conversational coding interface advertised. |
| `mistral-embed-2312` | completion_chat=false; no general conversational coding interface advertised. |
| `mistral-embed` | completion_chat=false; no general conversational coding interface advertised. |
| `mistral-moderation-2603` | completion_chat=false; advertised service capabilities: moderation, classification. |
| `mistral-ocr-2512` | completion_chat=false; advertised service capabilities: ocr. |
| `mistral-ocr-3-0` | completion_chat=false; advertised service capabilities: ocr. |
| `mistral-ocr-3` | completion_chat=false; advertised service capabilities: ocr. |
| `mistral-ocr-4-0` | completion_chat=false; advertised service capabilities: ocr. |
| `mistral-ocr-latest` | completion_chat=false; advertised service capabilities: ocr. |
| `mistral-ocr-4` | completion_chat=false; advertised service capabilities: ocr. |
| `mistral-ocr-4-1` | completion_chat=false; advertised service capabilities: ocr. |
| `voxtral-mini-2602` | completion_chat=false; advertised service capabilities: audio_transcription. |
| `voxtral-mini-latest` | completion_chat=false; advertised service capabilities: audio_transcription. |
| `voxtral-mini-transcribe-realtime-2602` | completion_chat=false; advertised service capabilities: audio_transcription_realtime. |
| `voxtral-mini-realtime-2602` | completion_chat=false; advertised service capabilities: audio_transcription_realtime. |
| `voxtral-mini-realtime-latest` | completion_chat=false; advertised service capabilities: audio_transcription_realtime. |
| `voxtral-mini-tts-2603` | completion_chat=false; advertised service capabilities: audio_speech. |
| `voxtral-mini-tts-latest` | completion_chat=false; advertised service capabilities: audio_speech. |

Two chat-capable audio records, `voxtral-small-2507`, `voxtral-small-latest`, stay outside the initial general coding matrix.

## Public evidence and comparison limits

[The Small 4 card](https://docs.mistral.ai/models/mistral-small-4-0-26-03) links `mistral-small-2603` to 119B total / 6.5B active. Direct/Aristote `mistral-small-4-119b` is **model-family-only**. Albert/Aristote Small 3.2 remains a separate pair; no fixed direct Small 3.2 ID appears in this account catalog. NVIDIA/direct GLM 5.3 is not currently executable.

[The Codestral card](https://docs.mistral.ai/models/codestral-25-08) reports **128k** context; the owner catalog reports **256000**. The discrepancy is unresolved. No exact expansion of k, serving ceiling or explanation is guessed. Both are recorded in `providers/mistral/evidence/2026-10-08-public-model-cards.json` with an exact digest of that authored observation file. Remote HTML is not archived by that digest. The 32768/4096 local caps are `benchmark_extension_provisional_common_cap`.

## Validation and unknowns

Added `scripts/mistral_catalog.py`, `tests/test_mistral_catalog.py`, three profiles, authored public evidence and an unperformed `runtime/preflight.mistral.example.json`. Updated workspace/runtime-lock selection, provider integration tests, Aristote observation metadata/tests and public documentation. CI discovers the new tests automatically.

Historical validation at the Mistral integration: **65 infrastructure tests passed**, including the then **13 active configs**, exact snapshot/fixture/prompt hashes, valid alias-ID overlap, reciprocal/card consistency, capability filtering, stable-ID selection, drift rejection, raw-field retention, evidence conflicts, CLI paths and schemas. The public baseline remains **2 passes, 1 intended failure**. `git diff --check` and local Markdown-link checks pass. GitHub CI was not executed in this session.

Mistral preflight is wholly not_run and scored_ready=false. Served checkpoints, revisions, quantization, tokenizer, decoding, actual pricing, output ceilings, runtime tool reliability/latency/throughput, exact release chronology, runtime observations and routing proofs remain null. Catalog capabilities are advertised only. No toy tasks, scored campaigns, sandbox or Level 2/3 work was performed.

Aristote standard Qwen has an owner-reported restricted basic observation: loading, expected trivial response, file creation and a pwd request using permitted tools without shell execution/stdout. Times, hashes, lock/effective-config linkage and routing proof remain null. The formal template is unchanged and not scored-ready.

For the owner's first Mistral smoke observation, follow [the exact manual steps](preflight-mistral.md). Complete formal qualification and OS isolation remain separate future gates.
