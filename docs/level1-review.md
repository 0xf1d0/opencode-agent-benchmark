# Level 1 implementation review — 2026-10-08

This records the previous infrastructure phase. Subsequent Aristote catalog
qualification and the owner-reported Albert basic observation are recorded in
[the current provider inventory](../providers/README.md); the historical counts
and qualification statements below describe the earlier review state.

## Changes

- Updated `.gitignore`, `AGENTS.md`, `DESIGN.md`, `METHODOLOGY.md`; added root
  `README.md`. Updated `references/tp/README.md` for local-only source provenance.
- Updated `providers/README.md` and all four provider `metadata.json` files.
  Preserved the owner's `providers/albert/catalog-snapshots/2026-10-08.json` bytes.
- Added Albert `<canonical-id>/opencode.json` for `qwen3-coder-30b-a3b-instruct`,
  `gpt-oss-120b`, `deepseek-v4-flash-0731`,
  `mistral-small-3-2-24b-instruct-2506`. Removed obsolete Albert root
  `opencode.json` / `opencode.env.json`; removed the optional Aristote env profile
  in favor of the owner-observed OpenCode-managed credential mode.
- Updated `scripts/create_workspace.py`; added `scripts/albert_catalog.py` and
  `scripts/runtime_lock.py`. Preparation now selects Albert by canonical ID and
  records the catalog hash outside the agent workspace.
- Added `schemas/preflight.schema.json`, `schemas/runtime-lock.schema.json` and
  `runtime/preflight.albert.example.json`. Updated `schemas/result.schema.json`
  to 1.1.0 with track/runtime/preflight artifacts and separate human behavior notes.
- Updated `docs/result-schema.md`, `docs/workspaces.md`; added `docs/preflight.md`,
  `docs/runtime-pinning.md`, `docs/runtime.md` and this review.
- Added `requirements-dev.txt`, `requirements-ci.lock` and
  `.github/workflows/infrastructure.yml`. Updated the two existing infrastructure
  test files; added `test_albert_catalog.py`, `test_repository_integrity.py` and
  `test_runtime_lock.py` under `tests/`.

The owner's previously staged Python-cache removals were left untouched. Fixture,
public test, oracle and prompt bytes were not modified. No commits were created.

## Albert evidence

Snapshot SHA-256:
`0fc3ed2b2fc5c581a1d175cd6a98cb9b64c85bb850431eb1990650f5c5ab1e0e`.
Source: owner-authenticated `GET https://albert.api.etalab.gouv.fr/v1/models`,
2026-10-08; exact retrieval timestamp is null.

The six inference candidates discovered are the four configured IDs above plus
optional `ministral-3-8b-instruct-2512` and `gemma-4-31b-it`. The other five canonical
IDs remain in raw provenance and are excluded:

| ID | Reason |
| --- | --- |
| `bge-m3` | Embeddings |
| `bge-reranker-v2-m3` | Reranking |
| `qwen3-vl-embedding-8b` | Embeddings |
| `whisper-large-v3` | Speech recognition |
| `lightonocr-2-1b` | OCR specialization |

`Mistral-Medium-3.5-128B` is absent and retired as an active Albert candidate.
Aliases are never model IDs. Mistral Medium direct remains configured.

## Validation

Executed locally:

```sh
PYTHONDONTWRITEBYTECODE=1 /tmp/opencode-benchmark-validation/bin/python \
  -m unittest discover -s tests -v
git diff --check
```

**41 infrastructure tests passed**, including all eight active provider configs,
workspace creation, canonical/alias rules, type filtering, snapshot/fixture/prompt
hashes, schema positive/negative cases, runtime lock drift/overwrite checks,
secret-free config consistency and cache ignore rules. The copied public fixture
ran with exactly **2 passes and 1 intended palindrome-space failure**. Local
Markdown file-link checks found no missing targets. Schema and documentation test
issues found during development were corrected before the final passing run.

Observed environment: Python 3.14.4, pytest 8.4.2, jsonschema 4.19.2,
Git 2.53.0, Linux 7.0.0-38-generic. Installed OpenCode version remains **null**:
no safe current version observation was made. Synthetic release strings in
infrastructure tests are not installed-version claims. GitHub CI was added but
not executed on GitHub in this session.

Dependency installation initially failed under sandbox DNS; the approved temporary
virtual-environment installation then succeeded. No provider calls, credential
inspection, benchmark submissions or scored runs occurred.

## Qualification and remaining gates

Albert has owner-account catalog evidence only. NVIDIA and Mistral have documented
identifier evidence; Aristote has supplied documentation with current catalog
unverified. Every runtime/inference/tool/permission/routing preflight is unperformed;
all cells remain `scored_ready: false`. Credential usability and storage location
remain null. Exact checkpoints, revisions, quantization, decoding, output ceilings,
latency, throughput and tool reliability remain null; hosting/certification/retention
claims are not inferred from nationality or performance.

Before first owner preflight: review the proposed controller/command/evaluator
boundaries, select an exact release and artifact, implement/audit the runtime after
approval, isolate effective configuration and external authentication, and freeze
synthetic non-task qualification probes. Start with Albert Qwen Coder.

Before first scored campaign: qualify each exact cell/track; freeze clean Git and
runtime/input locks, budgets/settings/retries/schedule; implement safe external
collection and evaluation; independently review contracts/oracles/human rubrics;
resolve source/fixture release rights. Statistical reporting remains planned.
Restricted profiles are implemented; the agentic sandbox is designed only.
Levels 2/3, sandbox implementation and scored campaigns remain outside this change.
