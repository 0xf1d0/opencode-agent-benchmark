# Benchmark Methodology

## Status, lineage and experimental unit

This protocol is proposed and must be frozen before scored runs. No runs have
occurred. [DESIGN.md](DESIGN.md) maps TP concepts to PDF pages and defines the
architecture. The reference is
[TP_IA_INTRO_26_27.pdf](references/tp/TP_IA_INTRO_26_27.pdf), identified there by
SHA-256; it is locally available and currently excluded from Git.

**Taken from the TP:** toy exercises, initialization and guide review, repair,
natural-language implementation, tests, ambiguity and undo, model comparison,
Git exploration, merged-PR reconstruction, prompt journaling, critical review,
and sovereignty/responsibility discussion (pp. 1–6, 11).

**Benchmark extensions:** scored contracts, independent oracles, provider matching,
sovereignty evidence profiles, unattended execution, fixed budgets, repeated
trials, statistical analysis, runtime isolation and public artifact releases.
The TP is a human pair-work exercise; unattended evaluation changes that setting
and cannot establish effects on student learning or human productivity.

The experimental unit is one task scenario × provider deployment/model × protocol
track × repetition. A workflow scenario may contain scripted steps; its steps are
not independent trials. Pin the OpenCode runtime, harness, task, environment,
inference settings and instruction versions. Codex participates only in
infrastructure maintenance outside runs and is excluded from execution, adaptive
prompting, repairs and grading.

## Task admission and splits

Each task needs a stable ID, source lineage, explicit observable contract,
agent-visible inputs, allowed edits, budget class and evaluator version. Review
tasks before comparing providers. Record all candidate exclusions with reasons,
including installation failures, flaky tests, ambiguous acceptance criteria,
unavailable source material or redistribution restrictions.

Split pilot/development tasks from scored tasks before tuning prompts or budgets.
Freeze membership and selection strata: level, task type, size and domain. Keep
related PRs from one repository together when splitting to limit leakage. Report
the complete candidate pool and admission process. Do not pick tasks based on a
provider's observed success. Equal weights within declared strata and separate
level reports are the default; any combined weighting must be frozen in advance.

### Level 1 contracts

Create new fixtures inspired by the TP; the original archive is absent. Define
normalization, punctuation, Unicode and empty-input behavior explicitly wherever
required by a fully specified task. Each specification variant begins from a
fresh snapshot. The benchmark must not silently reward requirements absent from
an underspecified prompt.

For test generation, evaluate submitted tests against the reference implementation
and a curated, pre-reviewed set of non-equivalent mutants. Report validity,
meaningful assertions, edge-case rubric, and the fraction of eligible mutants
killed. Timeouts/infrastructure faults are not automatic mutant kills. Line
coverage is descriptive, not proof that generated tests check behavior. Generated
tests cannot replace the external correctness oracle for code tasks.

For initialization, grade factual claims against a frozen repository fact sheet:
correct structure, executable commands, applicable conventions and invented
facts. Use a task-specific rubric with anchored 0/1/2 ratings (incorrect or absent,
partly supported, accurate and actionable). Report category scores and unsupported
claims separately; document each rating with evidence.

For ambiguity, use a fixed initial request and a published decision tree for
follow-ups. Responses to clarification questions must come from that tree; if a
question falls outside it, return a fixed neutral response and record it. Grade
clarification, assumption disclosure, scope and preservation of existing behavior.
Do not infer a desired speedup from the TP's example or require a particular fix.

For undo, prescribe a reversible edit and a fixed undo step regardless of model
quality. Exercise OpenCode's own supported undo mechanism. Compare pre-edit and
post-undo tracked and untracked files, contents, modes, HEAD/index and status;
record the exact restoration scope. Measure session rollback separately if the
pinned release supports it. External side effects are prohibited. A harness reset
can clean up a run but cannot count as successful agent undo. If native automation
is unsupported, publish this capability as unavailable rather than simulate it.

### Level 2 contracts

Supply a reproducible local Git history and issue snapshots; no live issue lookup
is needed. Specify branch naming and allowed commit scope in advance. Check the
base/ancestry, branch, commit contents, unrelated-file preservation and worktree
state as well as external tests. Describe any seeded unrelated changes explicitly
in that task's contract. Do not infer preservation of an unspecified worktree.

Independent task trials and multi-step workflow trials have separate reports.
Workflow carry-over is intentional only within that scenario; no history or
generated guide carries between repetitions or deployment cells.

### Level 3 reconstruction

1. Verify the PR is merged and record repository URL, license, PR ID, merge
   timestamp, merge method, exact base and reference commits, and archived source
   hashes. Source-document examples remain unverified until this check.
2. Inspect the actual merge topology. For a merge commit, assess its first parent
   as the pre-merge baseline; for squash or rebase, identify the state before all
   included changes. If unrelated changes prevent isolation, curate and disclose
   an adaptation or exclude the task. Record the reasoning for the selected base.
3. Reconstruct the request from information available before the solution.
   Remove solution diffs, corrective commit messages, post-fix comments and answer
   hints. Keep a provenance record of every included or excluded source fragment.
4. Pin dependencies and runtime; ensure evaluation is reproducible without live
   external services. Archive permitted dependencies or identify immutable
   retrieval sources. Exclude tasks requiring secrets or unavailable infrastructure.
5. For bug fixes, demonstrate the targeted oracle fails on the base and passes on
   the reference. For features, demonstrate a discriminating requirement missing
   on the base and satisfied on the reference. For refactors, both versions must
   pass behavior tests; add independently reviewed structural criteria that the
   base fails and reference satisfies. Baseline tests and expected failures are
   recorded, not assumed all green.
6. Keep external tests, reference patches, PR answer metadata and future Git
   objects outside the run. Expose only required pre-change ancestry in Git tasks;
   reconstruct a clean visible repository and audit reachable and unreachable
   objects. Merely checking out an older commit does not prevent answer leakage.
7. Have a human reviewer validate contract sufficiency, oracle discrimination,
   licensing and acceptable alternative solutions before task admission.

Code similarity to the merged patch is exploratory evidence only. Different code
that satisfies the contract may succeed; matching code with failing behavior does
not. Training contamination cannot be ruled out from runtime isolation alone.

## Provider eligibility and sovereignty

Evaluate NVIDIA Build, Mistral AI direct, Albert and Aristote through OpenCode.
Before scored runs, freeze an account-specific eligibility matrix covering model
availability, tool-call round trips, error handling, context/output limits,
reasoning controls, authentication, quotas, and observable usage. Probes contain
no scored task solutions. Access failures are documented, never bypassed through
an undeclared provider. Eligibility is determined without seeing scored outcomes.

Use two explicitly separate tracks if needed:

- **Controlled comparison:** common supported settings, tools and resource policy
  within each matched block. Unsupported controls are marked unknown; the block
  is not called fully controlled when equivalent settings cannot be established.
- **Deployment defaults:** declared provider-native settings with the same tasks
  and operational limits. This compares usable deployments and includes serving
  differences. It is never pooled with the controlled track.

The first scored release should prioritize the controlled track. Within a
provider, varying models supports comparison A. Across providers, use identical
verified model releases when possible, otherwise label family/variant differences
or model confounding. Do not fabricate common-family cells. Quantization,
tokenizers, chat templates and serving engines can differ even within a family.

For comparison D, build dated evidence cards for the **tested deployment**, with
sources and `verified`, `claimed`, `unknown` or `not applicable` status per field:
operator/control, compute and storage locations, subcontractors, applicable
jurisdictions, retention/training policy, access controls, certification scope,
model/license ownership, portability, and egress destinations. Documentation
claims are not independent certification checks. Include evidence dates and
limits; refresh at release time. Publish a multidimensional comparison rather
than a sovereign/non-sovereign score. Do not conclude sovereignty from coding
performance, provider nationality or a model's origin.

### Applying the supplied Aristote documentation

The candidate inventory and provenance are recorded in
[DESIGN.md](DESIGN.md#aristote-documented-integration-and-candidate-models).
Treat the supplied technical page as documentation evidence, separate from the
TP and from observed run capabilities. Preflight must still verify authentication,
account-specific model access, tool-call round trips, long-task behavior and
observable usage through the pinned OpenCode CLI.

Keep local OpenCode budgets distinct from actual service ceilings. The excerpt's
32,768-context/4,096-output settings apply to Qwen Reasoning High and the two
Mistral configurations; they are not verified endpoint maxima. `/v1/models` may
provide catalog evidence but cannot establish those maxima according to the
documentation. Seek dated DISI evidence for quotas and service limits and retain
unknowns where no evidence exists. Any common comparison cap is a separately
declared experimental choice, validated for every cell in its block.

The documentation's recommendation to switch to standard Qwen or Gemma after
GPT OSS HTTP 400 or Mistral Medium HTTP 500 is interactive troubleshooting advice.
**Do not apply that model substitution inside a scored run.** Log the error and
use only the frozen retry policy. If another model is tested, schedule a separate
declared cell; preserve the original failure. Intermittent access discovered
after eligibility freeze remains visible in the operational-success denominator.

Do not interpret `reasoning-high` as a portable reasoning-effort setting or
`mistral-medium-latest` as an immutable release. Verify variant identity and alias
resolution where possible; otherwise mark them unknown and limit matched-model
claims. The presence of `mistral-small-3.2-24b` makes Mistral-family matching a
candidate investigation, not an established overlap with another provider.
`gpt-oss-120b` is a documented model candidate, not a Codex agent; the Codex
runtime exclusion still applies independently of model naming.

Pin CLI major/minor version, configuration schema, provider key format and
credential-storage behavior. The Desktop configurator merges existing state and
does not test connectivity; successful configuration is not an eligibility test.
Prepare clean version-specific state and verify the effective configuration
instead of inheriting a desktop setup. The supplied page does not establish
French sovereign-cloud classification; obtain the separate deployment evidence
defined above before making that claim.

## Run protocol and controls

1. **Freeze:** record experiment/task versions, matrix, prompt language/text,
   instruction policy, budgets, repetitions, randomization seed, retry rules,
   exclusions, weights and statistical contrasts before scored execution.
2. **Prepare:** create a disposable sandbox from the pinned base/image. Verify
   source and oracle hashes and baseline outcomes. Mount only visible inputs;
   keep the evaluator, benchmark root, reference answers and other runs inaccessible.
3. **Configure:** isolate OpenCode state, caches, environment and configuration
   lookup. Disable automatic updates, optional plugins, MCP, web access, fallback
   models and subagents in the primary track. Enumerate repository-local tools and
   inherited instructions. Preserve and hash applicable upstream instructions;
   add only the declared fixed guide. Record the effective configuration.
4. **Execute:** start a new OpenCode session and deliver frozen prompts or
   scripted follow-ups. No human/Codex hints, manual fixes or outcome-dependent
   prompt edits. Automated permission decisions follow a fixed sandbox policy.
   Only the chosen provider/model may supply inference, including any auxiliary
   summary, title or compaction calls: disable them or route to the same cell and
   account for them. Abort and classify any unexplained routing.
5. **Collect:** capture prompt/response/tool events, stdout/stderr, provider errors,
   timestamps, session identifiers, patches and Git snapshots. Preserve raw
   private evidence before any redaction. Trace omissions are explicit.
6. **Evaluate:** stop the agent, transfer the final submission into a fresh
   evaluation environment, and run immutable external checks. Restore protected
   tests/runner settings or reject forbidden edits according to the contract.
   Apply separate Git/undo checks and human rubrics as appropriate. No feedback
   from sealed tests returns to the agent during the primary run.
7. **Report:** store termination reason, all outcomes, resource usage, missing
   values and artifact hashes, including failed and interrupted attempts.

Use French prompts initially as a declared design choice inspired by the French
TP, not a TP requirement. Translations form separate matched prompt variants.
For main coding trials use fixed guides; initialization and generated-guide
carry-over belong to separate tracks. Disable persistent memory and cross-run
caching of agent responses. Dependency caches may be shared only if immutable
and free of session state or answers.

Sandbox egress permits only the selected inference endpoint and declared essential
service dependencies; preinstall task dependencies and evaluate offline. Restrict
credentials to runtime authentication, preferably through an isolated forwarding
boundary, and prevent task shells from reading secrets. Run repositories and
generated code as untrusted input with filesystem, CPU, memory and process limits.
Log destinations and actual routing; a configured endpoint alone is insufficient
to prove the sovereignty profile of all data flows.

### Budgets, repetitions and failures

Before the scored release, use disjoint pilots to choose numeric per-class limits
for agent wall time, inference requests, tool actions, output/context settings,
CPU/memory, and evaluator time. A scored manifest missing these values is invalid.
Use the same declared limits within a comparison block. Record actual spend and
usage; do not secretly equalize outcomes by giving slower cells extra attempts.
Equal operational budgets do not establish equal compute or equal tokenization.

Proposed starting point: **five independent repetitions per task/cell**, finalized
after pilot precision and cost analysis. One scored attempt is one first-attempt
sample, not best-of-five selection. Randomize provider order within task/repetition
blocks and distribute blocks over time. Record schedule and timestamps to expose
load/time effects. Record requested temperature/seed and whether the endpoint
honors them; even deterministic-looking settings do not guarantee exact replay.

Bounded transport retries are permitted only under a predeclared rule for
recoverable failures. Preserve every request, backoff, request ID and uncertainty
about whether a timed-out request was billed or executed. No silent whole-run
restart. Any replacement attempt has a new ID linked to the original and is
reported separately from first-attempt results.

Classify outcomes separately: functional failure, budget exhaustion, provider
error/rate limit, OpenCode/tool failure, harness/evaluator fault, invalid task,
protocol violation or missing trace. Diagnoses need evidence. Scored-attempt
operational success uses all scheduled eligible first attempts as its denominator;
undelivered attempts count as non-success. Also show functional outcomes among
evaluable submissions with their denominator. Retain outages in the operational
view. Predeclared invalid-task exclusions apply to every cell, with sensitivity
results and a public reason log. If the submitted patch corrupts tests or hangs
evaluation, that is an agent outcome, not automatically an evaluator fault.

## Outcomes, review and analysis

Report separate level/task-type outcomes; avoid a single unqualified leaderboard.

| Outcome | Measurement |
| --- | --- |
| Functional correctness | All required immutable tests/contract checks pass; targeted success and regression preservation also reported separately |
| Generated tests | Validity on reference, mutant detection with explicit denominator, edge-case review; coverage descriptive |
| Guide quality | Fact-sheet rubric and unsupported-claim count |
| Git workflow | Base/branch/commit/worktree assertions, separate from code correctness |
| Ambiguity and undo | Evidence-backed behavior rubric; exact declared restoration checks |
| Efficiency | Agent elapsed time including retries, preparation/evaluation separately, requests/tool actions, measured usage and cost provenance |
| Reliability | Delivery rate, termination reasons, recoverable errors, unavailable cells |
| Critical errors | Evidence-linked taxonomy and reviewer decisions |

Usage unavailable from a provider is `unknown`, not zero. Keep billed usage,
OpenCode estimates and local token estimates distinguishable. Costs need a dated
price source or invoice evidence; promotional credits are not general market
prices. Report timeouts as censored durations rather than completed-task latency.
Provide latency for all attempts plus conditional latency for successes; the
latter alone introduces survivorship bias.

Human review occurs after submissions are frozen and cannot alter run prompts or
patches. Mask model/provider labels where feasible. Use two independent reviewers
for qualitative scored items, report agreement and adjudicate disagreements.
Taxonomy: invented API/dependency, false claim about repository/tests, misunderstood
requirement, regression, unsafe action, inadequate tests and unsupported sovereignty
claim. Distinguish a grounded failed hypothesis from an unsupported factual claim.
Each annotation links to an event, diff or validation result. The TP asks students
to describe at least two errors; our benchmark records observed errors without
manufacturing a minimum count. Human accept/modify/reject judgments from the TP
journal become post-run annotations, not online assistance.

Primary estimates are per-cell mean first-attempt success across tasks, and
predeclared paired differences on **the shared eligible task set**. Average repeats
within each task before aggregating; also publish all trial-level data. Use 95%
cluster-bootstrap intervals, resampling tasks for independent toy/Git scenarios
and repositories for real-world tasks while retaining matched cells and repeats.
Report task/repository counts, interval method, analysis seed and uncertainty. With
too few independent clusters, show descriptive estimates and avoid strong
significance claims. Do not treat repetitions or workflow steps as independent
evidence of generalization. Predeclare primary contrasts; label additional
comparisons exploratory and adjust multiple tests if significance tests are used.
Show full and common-task results, failure/exclusion sensitivity, and subgroup
counts. No effect across all providers is identifiable from a disconnected model
availability matrix without additional assumptions.

The TP's estimated time without AI (p. 11) is subjective reflection. This benchmark
cannot claim a measured productivity gain without a separately designed and
approved human baseline. Cost, latency and task completion are operational metrics.

## Threats to validity

| Threat | Consequence | Mitigation and remaining limitation |
| --- | --- | --- |
| Training contamination / public PR recall | Memorized fixes resemble reasoning | Record PR dates/popularity, vary original toy tasks, document exposure; model training data remain unknown |
| Solution leakage from Git, tests or metadata | Agent sees answers during run | Audit visible files and all Git objects, isolate oracles, deny web; public releases increase future exposure |
| Model/provider/quantization confounding | Incorrect attribution to provider | Match verified identities, disclose unknowns, separate family variants; opaque serving stacks prevent complete control |
| Provider drift and changing aliases | Comparisons change over time | Prefer versioned IDs, capture evidence/date, rerun as new releases; hosted weights may remain unverifiable |
| OpenCode/tool differences | Harness effects mistaken for model effects | Pin runtime and tools, verify effective config, disclose compaction; conclusions apply to that release |
| Prompt, language and guide sensitivity | Rankings depend on wording/context | Freeze matched variants, separate guide tracks; finite prompts cannot establish universal ordering |
| Incomplete or self-generated oracles | Incorrect solutions pass; tests mirror bugs | External tests/mutants, independent human review, protected evaluator; test completeness remains limited |
| Ambiguous requests | Hidden requirements penalize reasonable responses | Score assumptions/questions and preservation, publish follow-up tree; qualitative judgment remains |
| Selection and ecosystem bias | Easy Python tasks overstate general capability | Publish candidate/exclusion logs and strata, separate levels; initial scope does not represent all software |
| State carry-over and cache leakage | Later cells receive extra information | Fresh sessions/workspaces, audited caches, separate workflows; provider-side cache behavior may be opaque |
| Nondeterminism, outages and quota/load | Noisy rankings and missing data | Repeated randomized blocks, all-attempt logs, explicit denominators; service conditions vary |
| Unequal budgets / token accounting | Efficiency comparisons are misleading | Common operational caps, capability disclosure, usage provenance; equal tokens are not equal compute |
| Reviewer and maintainer bias | Subjective scores favor expectations | Frozen rubrics, independent blinded review, adjudication; infrastructure authors can still shape tasks |
| Artifact redaction or unavailable dependencies | Public replay loses evidence | Hashes, explicit redaction/missingness, pinned sources and archive; API output and privileged access cannot be exactly reproduced |
| Sovereignty inferred from branding | Performance presented as compliance proof | Deployment-specific evidence and unknowns; benchmark does not certify legal or security compliance |
| Human-guided TP vs autonomous runs | Educational results misinterpreted | Label the protocol change and review role; no human productivity/learning inference |

## Public reproducibility and ownership

Publish benchmark/task versions, manifests, sanitized prompts/events, final patches,
oracle versions, source/image/dependency hashes, provider evidence, environment
specification, randomized schedule, all attempt statuses, evaluator outputs,
analysis code and aggregate results. Document preparation, execution and offline
evaluation separately: exact inference replay is not promised, but a third party
must be able to rebuild inputs and recompute scores from retained submissions.
Restricted Albert/Aristote access or expired hosted models is an explicit limit;
offline score reproduction must not require inference credentials.

Maintain the TP's ignored status until redistribution permission is established.
Public releases need a rights-cleared provenance summary and a legitimate source
access path; a local hash alone does not make the reference publicly accessible.
If access cannot be provided, label that source-reproducibility limitation. Preserve
upstream licenses and attribution for task snapshots and patches; choose explicit
licenses for original infrastructure, fixtures and published data before release.
Record Codex-assisted infrastructure authorship separately from OpenCode run
provenance. Responsibility for review and publication remains with maintainers.

Keep keys, auth files and sensitive raw traces outside Git/public artifacts. Publish
a documented redaction policy, hashes of sanitized artifacts, and reasons for
withheld material; private raw hashes may be retained for internal audit. Human
review must check release artifacts for secrets, personal data and licensing
restrictions. Do not send proprietary code in a public benchmark. A release should
include a result card describing supported comparisons, evidence gaps, threats,
and exactly which claims can be reproduced.
