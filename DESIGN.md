# Benchmark Design

## Status and scope

This repository implements Level 1 preparation and validation infrastructure,
not a benchmark runner. Materials under `benchmark/toy/` include:
the owner-supplied unsolved fixture, source public tests from TutoOpenCode, prompts
and separate oracle tests. Its public baseline is verified: two passes and the
intended space-handling failure; see the [Level 1 status](benchmark/toy/README.md).
Secret-free provider profiles and provenance now exist under `providers/`;
live provider qualification and scored runs remain unimplemented.

**System under evaluation:** a pinned OpenCode release operating with a declared
model through a declared inference provider and fixed environment. Results describe
that complete system; they do not isolate intrinsic model intelligence.

**Codex's role:** design, implement, and maintain benchmark infrastructure outside
runs. Codex must never execute tasks, generate adaptive run prompts, repair
submissions, route inference, or grade benchmark runs. Runtime orchestration and
automated scoring must be deterministic software; qualitative review is human.
No Codex process, credentials, plugin, model, or fallback may enter a run.

The root `AGENTS.md` is the infrastructure contributor guide. It must never be
injected into task workspaces. Only task-declared instructions, including a guide
produced by a separate initialization condition when applicable, may enter a run.

## Reference and provenance

The primary reference is the local-only `references/tp/TP_IA_INTRO_26_27.pdf`,
*Dominante INFONUM CentraleSupélec — 2026–2027*, 11 pages. Its SHA-256 is
`6089bc8bdb09fbaaedabba8a1c8919908882cc238e531c7740573c60468ab53f`.
Page references below use PDF page numbers. The PDF is intentionally ignored and
not distributed through this repository. Redistribution permission and a public
source access path are unresolved; the hash records provenance, not access rights.

The TP explicitly says it is a pedagogical exercise rather than an evaluation of
raw ILaaS model performance (p. 1). Turning its activities into scored, repeated,
public experiments is our extension. The TP's configuration example must not be
copied verbatim (p. 4); its endpoint and model names are historical source content,
not verified current provider configurations.

| Concept taken from the TP | Reference | Extension introduced by this benchmark |
| --- | --- | --- |
| OpenCode setup and checking generated `AGENTS.md` | §§3–3.2, pp. 2–4 | Pinned runtime, isolated initialization trials, factual rubric |
| Palindrome bug repair; progressively specified `word_frequency` | §3.2, p. 4 | Independent task variants, immutable fixtures, external correctness oracles |
| Generated tests and checking edge cases | §3.2, p. 5 | Mutation testing and protection against tautological tests |
| Underspecified optimization and undo | §3.2, p. 5 | Ambiguity rubric, scripted follow-ups, verified restoration |
| Same-prompt model comparison using temperature conversion | §3.2, p. 5 | Repeated model/provider matrix with matched conditions |
| Clone, history, issues, initialization, repair and tests | §3.3, p. 5 | Reproducible Git scenarios and repository-state assertions |
| Real tasks reconstructed before an already-merged PR | §§3.4–4, p. 6 | Verified merge provenance, sealed evaluation, leakage controls |
| Bug fix, feature with tests, legacy refactoring | §4, p. 6 | Stratified task registry and distinct acceptance criteria |
| Existing/new tests, review, prompt journal, error analysis | §2, p. 2; §5, p. 11 | Structured event records, evidence taxonomy, blinded review |
| Sovereignty, security, responsibility, code ownership | §1, p. 1; §5.2, p. 11 | Deployment-specific evidence cards and release policy |

The owner subsequently supplied the TP's `TutoOpenCode` archive, enabling exact
reproduction of its public Level 1 palindrome tests. The exercise Git repository
and its issue texts remain unavailable. Any new fixtures or oracle contracts
must be explicitly identified as adaptations or benchmark extensions.
The suggested upstream PRs (pp. 7–10) are candidate leads, not validated tasks.

## Questions and comparison matrix

| Comparison | Required design | Permitted interpretation |
| --- | --- | --- |
| A. Different models | Same provider, task set, OpenCode and budget where available | Model differences within that deployment |
| B. Different providers | Common tasks and budget; disclose each model | Deployment comparison; model/provider confounded if models differ |
| C. Same model family across providers | Verified family, release and variant metadata | Matched family comparison; exact-model claim only with adequate identity evidence |
| D. French sovereign-cloud deployments | Verified deployment evidence plus the same task protocol | Performance and operational trade-offs within documented sovereignty profiles |

Required providers are **NVIDIA Build**, **Mistral AI direct**, **Albert**, and
**Aristote**. Every release must publish an eligibility matrix covering all four,
including unavailable or incompatible cells and their reasons. Restricted access
does not justify silently replacing a provider or claiming universal access.

No common model family is assumed. Eligibility must be checked before scored
runs using official catalog evidence and account-specific capability probes.
Record provider model ID, upstream family/release, weights revision if exposed,
quantization, serving changes, context/output limits, tool-call support, reasoning
controls and unknown values. Similar display names do not establish identical
weights or inference settings. If no matched pair exists, comparison C is reported
as unavailable. No causal provider effect can be inferred from an unmatched pair.

Current documentation is supplementary technical evidence, separate from the TP:

- [NVIDIA API documentation](https://docs.api.nvidia.com/) describes cloud-hosted
  NIM endpoints. This design targets the Build-hosted service, not an independently
  deployed NIM instance.
- [Mistral's model catalog](https://docs.mistral.ai/models) is a source for candidate
  model identifiers; an authenticated preflight must establish actual availability.
- [DINUM's Albert overview](https://ia.numerique.gouv.fr/outils-ia/albert-api/) describes
  Albert as its OpenGateLLM instance. [Albert's official documentation repository](https://github.com/betagouv/doc.albert-api)
  describes sovereign hosting; verify applicability to the exact tested service.
- The [Aristote documentation site supplied by the TP](https://aristote.pages.centralesupelec.fr/aristote-user-docs/)
  could not be retrieved during the initial review. The user subsequently supplied
  the text of its **Détails techniques** page; the documented facts below come
  from that supplied text, not an independent retrieval or live service test.
  The owner subsequently supplied an authenticated 2026-10-08 catalog; it now
  governs candidate membership, separately from this historical integration text.

The web sources were consulted on 2026-10-07. The Aristote excerpt's publication
date and exact page URL were not supplied; record them when available. No live
provider calls were made.
French ownership, French model authorship, European hosting, and sovereign-cloud
operation are separate attributes. Mistral direct must not be classified as a
French sovereign-cloud deployment merely from the company's nationality. Albert
and Aristote are required candidates; classification requires deployment evidence.

### Aristote: documented integration and candidate models

This supplementary documentation establishes an OpenAI-compatible API at
`https://llm.aristote.education/v1`, chat path `/chat/completions`, and bearer-key
authentication. It recommends `qwen-3.6-35b-instruct` for starting out; this is a
service recommendation and the configured candidate default, pending runtime qualification.

The following table preserves **historical documentation** provenance, not the
active catalog matrix. The owner snapshot below governs current candidates.
`gpt-oss-120b` is absent from that snapshot and has no active Aristote profile.

| Documented model ID | Documentation status | Benchmark treatment |
| --- | --- | --- |
| `qwen-3.6-35b-instruct` | OpenCode conversation; default recommendation | Candidate pending agentic capability probes |
| `qwen-3.6-35b-instruct-reasoning-high` | Qwen Reasoning High variant; OpenCode conversation | Separate cell; reasoning behavior/settings require verification |
| `gemma-4-31b` | OpenCode conversation | Candidate pending agentic capability probes |
| `gpt-oss-120b` | OpenCode conversation; intermittent access; HTTP 400 mentioned | Candidate with documented reliability caveat; not Codex |
| `llama-3.1-8b` | OpenCode conversation | Candidate pending agentic capability probes |
| `mistral-small-3.2-24b` | OpenCode conversation | Candidate for cross-provider family matching, not a confirmed match |
| `mistral-medium-latest` | OpenCode conversation; server error; HTTP 500 mentioned | Candidate with reliability and mutable-alias caveats |

`bge-m3` and `bge-reranker-v2-m3` are documented as embedding and reranking
models. They are outside the coding-agent comparison matrix. Conversation support
does not establish successful tool calling or long agentic workflows: the supplied
documentation explicitly calls for case-by-case testing.

For Qwen Reasoning High and both Mistral models, the documented OpenCode `limit`
settings are **32,768 context tokens and 4,096 output tokens**. These are local
configuration budgets, not service ceilings. The documentation says `/v1/models`
does not expose those ceilings; they require confirmation from CentraleSupélec's
DISI. Other model ceilings and quotas remain unknown from this excerpt. Record
configured budgets and evidenced service limits separately; do not automatically
apply these values to other models or providers.

The manual Desktop configuration uses OpenCode 2's `providers` format. The
automatic configurator uses format 1 when no `providers` section exists, to retain
CLI 1 compatibility; the documentation says OpenCode 2 also reads format 1.
Credential storage is an external OpenCode implementation detail. Never inspect
or copy it. Pin the actual CLI release and test project configuration behavior;
Desktop compatibility is not proof of CLI compatibility for that release.

The configurator preserves existing connections, settings, manual models and
credentials, and **does not test the service connection**. It is therefore not a
benchmark preflight or a substitute for isolated effective configuration. No
configurator is executed. Versioned provider profiles are maintained separately.
The excerpt provides no deployment-specific hosting, certification, retention,
or model-weight identity evidence; those verification gates remain open.

## Current Level 1 provider matrix

All committed profiles implement the **restricted** no-shell track. None is
`scored_ready`. The first owner-driven Albert preflight selects
`qwen3-coder-30b-a3b-instruct`. The owner's authenticated 2026-10-08 catalog,
SHA-256 `0fc3ed2b2fc5c581a1d175cd6a98cb9b64c85bb850431eb1990650f5c5ab1e0e`,
is the authoritative account-specific evidence for that date. Four canonical
Albert configurations are implemented: Qwen Coder, GPT OSS 120B, DeepSeek V4
Flash 0731 and Mistral Small 3.2. Ministral 3 and Gemma 4 remain optional. Embedding,
reranking, ASR and OCR models are excluded with reasons in provider metadata.
Aliases are provenance only; workspace selection never resolves an alias.

`Mistral-Medium-3.5-128B` is retired from Albert because it is absent from that
snapshot. Mistral's owner catalog now excludes `zai-glm-5-3`; its former config
is retired. NVIDIA retains `z-ai/glm-5.3`, but that cross-provider GLM comparison
is historical/planned and not executable for the current owner account.

Mistral's exact owner snapshot contains 46 records, SHA-256
`4246145d5629c7106aaefe4e0831cd4d9e9178e868f3c3b9c5feaced36178373`.
Preferred cells are `mistral-medium-3-5`, `mistral-small-2603`, `codestral-2508`.
Seventeen alias-linked apparent card groups preserve returned IDs/aliases without
claiming checkpoint equivalence. Stable preferred IDs only enter the initial
matrix; 19 non-chat service records are excluded by capabilities and two audio-chat
records are not initial candidates. Four fixed optional models remain unconfigured,
including specialized Leanstral. Raw creation timestamps have unverified semantics.

Direct Small 4 / Aristote `mistral-small-4-119b` is model-family-only, supported by
[public direct-model evidence](https://docs.mistral.ai/models/mistral-small-4-0-26-03).
It does not establish identical served weights. Albert/Aristote Small 3.2 is a
separate pairing; the direct catalog has no fixed Small 3.2 candidate. Codestral's
catalog context 256000 conflicts with the public model card's 128k label; preserve
both sources without choosing a ceiling. The common 32768/4096 cap remains an
explicit benchmark extension. See [the evidence inventory](docs/mistral-review.md).

Aristote now has its own exact owner-authenticated snapshot dated 2026-10-08,
SHA-256 `ace8258a30778b5a7eaef0ce22e20bbe2c95c15ba1c4c9b495b7589586312e69`.
Its first preflight candidate is `qwen-3.6-35b-instruct`. Five restricted profiles
select that ID, its separate reasoning-high condition, `qwen-3.8-27b`,
`mistral-small-3.2-24b` and `mistral-small-4-119b`. Gemma/Llama are optional,
embedding/rerank entries excluded, and `mistral-medium-latest` retained only as a
floating alias, not a direct Medium 3.5 match. The single root profile is retired.

Raw `owned_by` and `created` are preserved without assigning upstream ownership
or release dates; missing `mode` is null. Conversation context/output limits,
served identity, quantization, tokenizer, decoding, tools and prices remain null.
The local 32768/4096 limits are provisional benchmark caps. Albert/Aristote Mistral
Small 3.2 remains **model-family-only**; no checkpoint identity is established.

The owner reports Albert Qwen3 Coder restricted basic inference and file editing
succeeded. This is an owner observation with missing dated evidence/runtime pins,
not full formal qualification. The owner also reports Aristote standard Qwen
loading, trivial inference and file creation succeeded; a `pwd` request produced
no shell execution/stdout and used permitted file/search tools. No evidence hash,
time, runtime linkage or routing proof is inferred. Formal templates remain
unperformed. Mistral has catalog evidence and its own unperformed Medium template.
No provider is scored-ready.

Authentication for all four IDs is `opencode_managed_persistent_credential`.
The owner reports that project-defined `albert` and `aristote` must be loaded for
those custom providers to appear in `/connect` and the model selector. Provider
IDs remain fixed. Storage location is null and unverified; credential usability
is null until an owner-driven preflight. No credential discovery belongs in the
infrastructure. See [provider evidence and qualification](providers/README.md).

## Three levels

### Level 1 — Controlled toy project

Propose a small Python project with pytest, reflecting the TP's teaching stack.
Include separate scenarios for initialization, diagnosis/repair, implementation
from specification, test generation, ambiguous optimization/undo, and same-prompt
model comparison. Palindrome, word frequency and temperature conversion are
source-derived themes; the public palindrome tests are source-exact; explicit contracts and hidden cases
are separately attributed benchmark additions.

Initialization produces `AGENTS.md` from a clean repository without that file.
Score factual project description, valid commands, useful conventions, and
unsupported assertions against a maintainer-authored fact sheet. Main coding
comparisons instead use one fixed task-specific guide. A separately labeled
end-to-end track may carry generated guides forward, measuring that additional
source of variation. Never mix these tracks in one ranking.

Specification variants start independently from the same base. Ambiguous requests
are assessed for questions, stated assumptions and behavior preservation; they
cannot be judged against an unstated desired implementation. Undo is a separate
OpenCode capability measurement, not a code-correctness score.

### Level 2 — Git workflow benchmark

Use a self-contained synthetic repository with curated history and local issue
snapshots. Exercise history inspection, issue diagnosis, branch creation, repair,
tests and a local commit. Branch/commit creation and additional Git checks extend
the TP's simpler workflow; push, merge and remote PR creation are excluded.

Maintain both independent scenarios for attribution and a separately labeled
multi-step workflow for cumulative behavior. Assert the intended base, branch,
commit contents, clean/expected worktree state, preserved unrelated files and
passing external tests. Correct code and correct Git state are separate outcomes.

### Level 3 — Real-world tasks from merged PRs

Curate licensed public repositories and already-merged bug-fix, feature and
refactoring PRs. Freeze a verified pre-change state, reconstruct a self-contained
request using pre-solution information, and keep the merged solution for offline
reference analysis. The human patch is not the only acceptable solution.

Verify actual merge topology and task boundaries rather than blindly using
`merge_sha~1`; squash, rebase and multi-commit PRs require explicit handling.
Admit a task only after reproduction and validation as defined in
[METHODOLOGY.md](METHODOLOGY.md). Start with a modest, reproducible Python subset;
broader languages and service-dependent tasks require new versioned strata.

## Proposed repository architecture

The tree below is the **proposed complete architecture**, rather than an inventory
of implemented files. Current Level 1 materials use `benchmark/toy/fixture/`,
`benchmark/toy/prompts/` and `benchmark/toy/oracle/`; adopting the generalized
task registry below is future work. Provider profiles now exist under `providers/`;
their live eligibility and effective runtime restrictions remain to be verified.

```text
AGENTS.md                         contributor guide, outside task workspaces
DESIGN.md                         architecture, provenance, implementation gates
METHODOLOGY.md                    experimental protocol and reporting rules
README.md                         public overview and reproduction entry point
LICENSE                           benchmark license, chosen before release
pyproject.toml                    proposed Python harness and development tools
<dependency lockfile>             chosen with the packaging tool
references/tp/                    source note; PDF remains locally ignored
docs/
  provenance.md                   rights, source digest, concept-to-source map
  task-authoring.md               admission rules, contracts, reviewer checklist
  provider-evidence/              dated service/model/sovereignty evidence cards
  decisions/                     versioned architecture decision records
schemas/                          task, provider, experiment, run, result contracts
tasks/
  level1/<task-id>/                manifest, prompt, visible inputs, attribution
  level2/<task-id>/                manifest, prompt, curated Git/issue inputs
  level3/<task-id>/                manifest, sanitized request, source provenance
evaluation/<task-id>/              sealed tests, reference patches, review rubrics
experiments/                      frozen matrices, budgets, repeats, ordering
providers/                        secret-free descriptors; no model defaults
src/opencode_benchmark/
  cli/                            prepare, preflight, run, evaluate, report
  registry/                       schema validation and eligibility resolution
  environments/                   pinned images, workspace and Git construction
  runtime/                        pinned OpenCode invocation and event capture
  providers/                      capability probes and config rendering
  evaluation/                     deterministic tests and state/rubric aggregation
  reporting/                      statistics, comparisons and evidence exports
tests/                            infrastructure unit, integration and isolation tests
containers/                       reproducible runtime and evaluator image recipes
scripts/                          thin maintenance/reproduction entry points
.github/workflows/                infrastructure checks; scored runs opt-in
runs/<run-id>/                    private raw evidence, ignored in Git
workspaces/                       disposable task worktrees, ignored in Git
cache/                            dependency/source cache, ignored in Git
results/<release-id>/              sanitized summaries and artifact index
```

Evaluation material may be public in a reproducible release but must remain
outside agent-visible mounts and Git objects. A public oracle is operationally
sealed during execution, not permanently secret; publication creates a documented
contamination risk for future releases. Large artifacts belong in a checksummed
release archive or durable artifact store with an index, rather than Git history.

The harness controls preparation, budgets and collection. OpenCode performs all
reasoning and code actions. A separate evaluator executes the resulting patch
against immutable oracles. The reporting layer consumes recorded results only.
Provider integration must preserve OpenCode's agent loop rather than implementing
a competing agent loop or calling models directly to solve tasks.

Future schema contracts must capture:

| Contract | Required information |
| --- | --- |
| Task | ID/version, level/type, TP lineage, prompt hash, source/base hashes, visible guide, environment digest, permitted edits, oracle/review IDs, rights |
| Provider | Service ID, endpoint identity, credential reference, model identity/evidence, capabilities, adapter revision, sovereignty evidence |
| Experiment | Eligible cells, task split, budgets, inference settings, repetitions, randomized schedule, exclusions, scoring/statistical plan |
| Run | Unique attempt ID, experiment/task/cell/repeat, OpenCode/harness revisions, effective config hash, timestamps, events, patch, termination reason |
| Result | Oracle outcomes, Git/undo/rubric outcomes, errors, costs with provenance, missingness, reviewer decisions, artifact hashes |

OpenCode supports programmatic invocation and session export according to its
[CLI documentation](https://opencode.ai/docs/cli/). Its
[configuration documentation](https://opencode.ai/docs/config/) says settings from
multiple locations are merged. Therefore the adapter must be tested against one
pinned release, capture the effective configuration, and isolate inherited user
settings. Exact init/undo automation interfaces remain a compatibility gate;
shell restoration cannot stand in for OpenCode undo.

## Implementation phases and acceptance gates

| Phase | Work after this design phase | Gate before proceeding |
| --- | --- | --- |
| 0. Design review | Agree scope, attribution, comparison claims, rights and protocol | Review runtime architecture and unresolved decisions before sandbox implementation |
| 1. Contracts and isolation | Schemas, provenance registry, pinned runtime adapter, sandbox, credential boundary, synthetic infrastructure tests | Verify config isolation, no Codex paths, all inference routing, event completeness, init/undo interfaces and deterministic evaluation |
| 2. Level 1 pilot | Source-attributed toy fixtures and rights review, external tests/mutants, ambiguity and guide rubrics | Immutable baseline validated; independent human oracle/rubric review; pilot separated from scored tasks |
| 3. Provider qualification | Integrate NVIDIA Build, Mistral direct, Albert, Aristote; capability and evidence cards | Publish eligibility matrix and unavailable cells; verify no hidden fallbacks or unrecorded auxiliary inference |
| 4. Level 2 | Curated Git history/issues, independent tasks, workflow track | Assert code and Git outcomes; verify restoration and leakage boundaries |
| 5. Level 3 | Verify candidate PRs, curate prompts, pin sources/dependencies and rights | Base/reference oracle checks, reproducible offline evaluation, no future-history leakage; human review per task |
| 6. Protocol freeze and evaluation | Separate pilot from scoring, freeze matrix/budgets/repeats, execute randomized paired trials | Pre-register before scored outcomes; archive every attempt and exclusion |
| 7. Public release | Sanitize evidence, publish artifacts, statistics, limitations and reproduction guide | Independent replay of preparation/evaluation; rights and disclosure review; all claims linked to evidence |

Open decisions are the exact OpenCode release, runtime packaging/image, accessible
model matrix, numeric resource budgets, final task count, independent review
capacity, source-document redistribution rights, and deployment sovereignty
evidence. These are gates to future implementation or publication, not assumptions
filled in by invented provider settings.

## Level 1 runtime architecture review gate

The implemented policy is `restricted`, with no model-controlled shell or web
tools. It does not reproduce the full local development behavior of the TP.
`agentic` is a separate proposed track allowing local Python, public pytest and
justified Git inspection inside an OS sandbox. No agentic profile, sandbox or
broker is implemented. [Runtime architecture](docs/runtime.md) evaluates namespace,
container and microVM options and defines acceptance attacks before selection.

### Threat model and filesystem boundary

Assume arbitrary code execution by submitted code/tests and malicious tool/path
arguments. Only the generated project and minimal read-only runtime dependencies
are visible. The benchmark repository, hidden oracle, evaluator, references,
maintainer files, catalogs, other runs and expected patches are inaccessible.
Prevent parent traversal, symlink escapes, host `/proc` access and inherited file
descriptors. No host/engine/control sockets enter the guest. Directory separation
and OpenCode permissions alone do not enforce this boundary.

### Process and credential boundary

The pinned OpenCode controller is separate from model-controlled command processes.
A trusted broker mediates every executable and file tool; wrapping only shell is
insufficient. Command processes cannot inspect controller processes, private
OpenCode state, memory, environment or descriptors. Authentication is an external
owner-managed concern; storage location remains null. Provisioning into a private
controller domain needs owner review and must not inspect/copy the maintainer's
credential store. Record the trusted adapter as part of the evaluated system.

### Network boundary and paths

Path A is controller-to-selected-provider inference, authenticated using private
OpenCode-managed state. Path B is broker-to-disposable-guest command execution,
with no Internet, host loopback, DNS, metadata or inference-proxy access. The guest
must not inherit the controller's network identity or any inference socket. OS
network enforcement blocks Python/generated-code requests as well as curl.
Freeze endpoint allowlists and auxiliary inference routing; log actual destinations.

### Evaluator and remaining limitations

After stopping the agent, a trusted supervisor exports inert checked files into
an independent offline evaluator sandbox. Oracle and reports never enter the
agent mount or feedback. Collection is external and immutable to the agent;
submitted code never executes on the collector host. Native initialization/undo
and implicit filesystem/Git operations require pinned-release audit; no harness
reset counts as OpenCode undo. Kernel escapes, controller/adapter vulnerabilities,
opaque provider behavior and public contamination remain residual risks.

[Offline locks](docs/runtime-pinning.md) now record exact selected runtime and
input provenance; [preflight records](docs/preflight.md) distinguish nine owner
checks from catalog availability. Both are infrastructure contracts, not evidence
of an implemented runtime or successful inference. Stop before sandbox
implementation until the owner reviews this architecture and selects a release.
