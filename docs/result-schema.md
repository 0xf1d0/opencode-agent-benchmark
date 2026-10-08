# Result schema

This is a proposed data contract, not a result collector, runner or scoring
implementation. [`schemas/result.schema.json`](../schemas/result.schema.json)
uses JSON Schema Draft 2020-12 and covers Level 1 only. All object fields are
required and unknown properties are rejected. JSON Schema distinguishes missing
properties from null values; see the [official object reference](https://json-schema.org/understanding-json-schema/reference/object).

## TP lineage and interpretation

The TP prompt journal (§5.1, PDF p. 11) records time, request, response/suggestion
summary, and accepted/modified/rejected decision with justification. The schema's
`interaction` object preserves these separately. TP §2 (p. 2) and §5.2 (p. 11)
provide the basis for tests, review, error analysis and responsibility. Provider,
model identity, hashes, repeated attempts, structured failures and measurements
are benchmark extensions, not fields claimed to exist in the TP journal.

One result represents one scheduled trial for a task, deployment and repetition.
Its `attempts` preserve first and replacement executions; scored analyses use
attempt 1 as the first-attempt outcome. Transport retries are API request events
inside an attempt, not new attempts. Independent repetitions have new trial IDs.
A provider/model/configuration change creates a new trial, not a retry. Native
initialization/undo are journal entries with `kind: native_command`; they are not
inference prompts. The seven task prompt IDs come from the versioned prompt
metadata; task IDs identify scenarios, not necessarily the same string.

## Missing values and evidence

Every required measurement field accepts `null`. No guesses, token estimates,
invented zeroes, string `"unknown"`, NaN or infinity. Identifier strings and known
protocol constants must be present to identify a record; nullable metadata must
still be explicitly provided. Nested measurement containers remain present;
nullable artifacts/event collections may be null as specified.

- `null`: unavailable, unmeasured, inapplicable or withheld; give a reason in
  `missing_measurements` when known.
- `0`, `false`, `[]` or `""`: known values, never missing-value substitutes.
  Empty arrays mean absence was verified; partial lists must be identified as
  partial capture and cannot establish total counts.
- A verified absent guide uses `before: []`; an unobserved guide uses `before: null`.
  A known empty patch uses an artifact with `inline_text: ""`.
- A test that did not run has `status: not_run`, with counts/exit/duration null;
  no recorded invocations may instead be `[]` when that absence is verified.
- Token aggregates are null if coverage is partial/unknown. Keep available partial
  request evidence in artifacts, not in fields claiming whole-attempt totals.
  Cache/reasoning categories can overlap input/output; do not add them together.

Review decisions express a human judgment, not an automated test result. In the
primary protocol review is post-run and cannot change the frozen patch. A modified
post-run proposal is a separate derived submission, not a replacement score for
this attempt. Online hints, edits, manual retries or configuration changes are
human interventions and may invalidate a primary-protocol run. Codex may maintain
this schema but must not execute, summarize via inference, repair or grade runs.

## Runtime and outcome categories

Version 1.1.0 adds required `protocol_track`, `runtime_lock`, `preflight` and
per-attempt `agent_behavior` fields. Earlier 1.0.0 records require an explicit
migration with null missing artifacts/reviews; never fabricate historical pins.

| Field | Type | Meaning |
| --- | --- | --- |
| `protocol_track` | restricted / agentic | Runtime action policy; separate reports, agentic design-only. |
| `runtime_lock` | artifact or null | Exact runtime-lock bytes; records OpenCode, benchmark Git, Python/pytest/Git, OS/image, config/catalog, fixture and prompt versions/hashes and run ID. |
| `preflight` | artifact or null | Owner-driven qualification record tied to this cell/runtime/track, null until performed. |
| `attempt.agent_behavior` | agent_behavior or null | Evidence-backed human behavior review, null before review. |
| `agent_behavior.relevant_files_inspected` | string array or null | Relevant workspace paths identified from the trace by a human reviewer. |
| `agent_behavior.useful_tool_call_ids` | string array or null | Human-reviewed useful tool-event IDs. |
| `agent_behavior.tests_executed_spontaneously` | boolean or null | Observed OpenCode-initiated tests without follow-up instructions. |
| `agent_behavior.unnecessary_changes` | string array or null | Evidence-linked human notes on out-of-scope edits. |
| `agent_behavior.unnecessary_complexity_notes` | string or null | Human assessment of avoidable complexity. |
| `agent_behavior.qualitative_reviewer_notes` | string or null | Separate post-run critical review. |

[Runtime fields](runtime-pinning.md) and [preflight fields](preflight.md) are
fully documented separately. Runtime locks are preparation evidence, not measured
execution proof. A collector must require equal execution provenance and preserve
any mismatch. Authentication internals are never part of results.

Functional reporting separates public and hidden pass rates, first-attempt success
and final task success. Behavior reports use the fields above, attempts and human
interventions. Operational reports retain duration/tokens/tool/provider/API errors,
rate limits and retries. The TP journal preserves exact prompts, summaries,
decisions and justifications. Sovereignty stays in separate provider evidence
cards, contributing no capability points. No aggregate score is defined.

## Artifacts, hashes and access

Prompt hashes cover the exact delivered UTF-8 bytes, including final newlines;
canonical prompt hashes must match `benchmark/toy/prompts/metadata.json`. A missing
or withheld prompt is null even if its original hash is known. Never put a
redacted paraphrase in the exact `prompt` field. Summaries are explicitly separate.

AGENTS.md snapshots refer to applicable task instructions, never the root benchmark
contributor guide. Patches include new/untracked file changes against the exact
attempt base. Git commit identifiers alone do not identify dirty or non-Git input
snapshots; archive those inputs and record the declared snapshot hash procedure.

Artifact hashes describe the retained bytes. Redacted artifact hashes therefore
refer to redacted content; they are not hashes of the original exact prompt.
Relative paths resolve against the result's artifact bundle. Store secrets nowhere
in public results; authentication headers must be removed from retained evidence.
Public and hidden tests are separate invocation lists. Hidden tests run only in
the evaluator after stopping OpenCode; their sources and reports must never be
mounted/copied into the agent workspace or delivered as feedback. Publish results
only after the appropriate disclosure/redaction review.

All timestamps are observed UTC RFC 3339 values ending in `Z`; all durations are
measured seconds and counts are non-negative integers unless otherwise stated.
Timeout durations are censored observations, not successful completion times.
`functional_success` is null until an applicable external contract supports a
boolean verdict; a failing expected baseline does not determine final success.

## Field reference

Each field below corresponds to a documented schema property.
All fields in each object are required. `T | null` permits an unknown value; a
reference to an object requires that object's fields whenever it is present.

## Root result

Proposed Level 1 result record: one scheduled task/deployment trial, preserving first and replacement attempts. No collection or scoring implementation is supplied.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `schema_version` | constant "1.1.0" | Result contract version. A field/meaning change requires a new schema version. |
| `result_id` | string | Unique identifier of this result document. |
| `experiment_id` | string | Identifier of the frozen experiment manifest defining budgets, eligibility and scoring. |
| `trial_id` | string | Unique scheduled task/deployment/repetition identifier; a replacement attempt stays in this trial. |
| `benchmark_level` | constant 1 | Only Level 1 is currently supported by this result contract. |
| `task_id` | string | Stable task/scenario identifier; independent of its prompt variant. |
| `task_version` | string \| null | Exact task contract/fixture version; null if unavailable. |
| `prompt_set_version` | string \| null | Exact prompt-set version from prompts/metadata.json; null if unavailable. |
| `provider` | string \| null | Exact declared service/deployment identifier; no API key or credential material. |
| `model_id` | string \| null | Exact requested provider model identifier, including variant/alias spelling; never a display-name substitute. |
| `resolved_model_id` | string \| null | Immutable model revision returned or documented for this deployment if independently observed; null if an alias cannot be resolved. |
| `model_family` | string \| null | Upstream family based on recorded provider/model evidence; null when identity is unknown. Do not infer from display-name resemblance. |
| `model_evidence` | array<artifact> \| null | Dated catalog/model identity evidence supporting family and revision; null if unavailable. |
| `opencode_version` | string \| null | Exact observed OpenCode CLI version including build/prerelease information; null if not measured. |
| `effective_config` | artifact \| null | Secret-free effective runtime configuration, including inference settings and auxiliary-model routing. |
| `number_of_attempts` | integer \| null | Measured total whole-run attempts for this scheduled trial, not API retries, interactions or independent repetitions. |
| `attempts` | array<attempt> \| null | All execution attempts in chronological order, including failed/replaced attempts; null if history unavailable. |
| `missing_measurements` | array<missing_measurement> \| null | Explanations for null/unavailable evidence; [] only when no explanation is needed or no reason is known. |

## artifact

Retained artifact descriptor. Null descriptor means the artifact is unavailable.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `path` | string \| null | Artifact-relative path or durable archive URI; never an instruction to mount it into the agent workspace. |
| `sha256` | string \| null | SHA-256 of the exact stored artifact bytes, including any redaction, not a guessed or original-content digest. |
| `inline_text` | string \| null | Exact retained UTF-8 text, including newlines; empty text is a known empty artifact. Null when not embedded. |
| `redacted` | boolean \| null | True if stored bytes were redacted, false if confirmed intact, null if provenance is unavailable. |

## instruction_file

An observed AGENTS.md file and its exact retained content.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `workspace_path` | string \| null | Observed path of this AGENTS.md, relative to the task workspace, or its declared external instruction location. |
| `artifact` | artifact \| null | Content/path/hash descriptor of the observed file; never substitute the benchmark contributor guide. |

## agents_md

Instruction state at attempt boundaries; generated instructions may vary by track.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `policy` | enum: absent, fixed, generated, null | Declared instruction policy. Null if the protocol record is unavailable. |
| `before` | array<instruction_file> \| null | All observed applicable AGENTS.md files before the attempt; [] only when their absence was verified. |
| `after` | array<instruction_file> \| null | All observed applicable AGENTS.md files after the attempt; [] only when their absence was verified. |

## git

Git provenance; fixture snapshots without Git commits use null commit fields.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `benchmark_commit` | string \| null | Full benchmark repository commit at preparation time; not the current branch name. |
| `benchmark_dirty` | boolean \| null | Whether benchmark inputs had uncommitted changes; null when not checked. |
| `benchmark_changes` | artifact \| null | Retained dirty-input changes, including an archive/index for untracked inputs; null if unavailable or not applicable. |
| `task_base_commit` | string \| null | Full task repository commit before this attempt; null for a fixture without Git history. |
| `submission_commit` | string \| null | Full task commit after execution, if observed. Does not imply worktree changes were committed. |
| `task_snapshot_sha256` | string \| null | Digest of the canonical prepared task snapshot; its hashing procedure must be declared in the experiment. |

## interaction

One user prompt or native command and its associated response/review, following the TP journal.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `interaction_id` | string | Stable identifier unique within this trial; not an inferred conversation turn. |
| `timestamp` | string \| null | UTC timestamp when this prompt/command was submitted, if recorded. |
| `kind` | enum: prompt, native_command, null | Whether this was inference input or a native command such as initialization/undo. |
| `prompt_id` | string \| null | Version-controlled prompt identifier; null for an uncatalogued prompt. |
| `prompt` | string \| null | Exact delivered UTF-8 prompt/command text, preserving whitespace; null if missing or withheld, never a paraphrase. |
| `prompt_hash` | string \| null | SHA-256 of exact delivered prompt bytes, including final newline. Must match the prompt-set digest for unchanged canonical prompts. |
| `response_summary` | string \| null | Evidence-grounded human or deterministic summary of the associated response. Null if no reliable summary exists; never Codex/LLM-generated during evaluation. |
| `response` | artifact \| null | Optional retained raw response/transcript artifact; separate from its summary. |
| `decision` | enum: accepted, modified, rejected, null | Human review decision about the AI suggestion, independent of tests; null means no recorded decision. |
| `decision_justification` | string \| null | Evidence-grounded reason for the decision; mandatory non-null when a decision is recorded. |
| `review_phase` | enum: during_run, post_run, null | When the review decision was made. Primary protocol permits post_run review only. |
| `reviewer_id` | string \| null | Pseudonymous human reviewer identifier; null when unavailable or no review occurred. |

## test_run

One actual test command invocation. Counts describe this invocation, not an invented aggregate.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `test_run_id` | string | Identifier unique within the trial, used to distinguish repeated test executions. |
| `phase` | enum: baseline, agent, evaluation, null | Baseline before execution, public feedback during agent execution, or evaluator after the agent stops. |
| `suite_id` | string \| null | Declared suite or task-specific oracle identifier; null if unavailable. |
| `suite_sha256` | string \| null | Digest of immutable suite inputs under a declared hashing procedure; null when not recorded. |
| `command` | array \| null | Exact command argument vector; null if the invocation was not captured. |
| `status` | enum: passed, failed, error, timeout, not_run, null | Observed invocation outcome; null if unavailable. not_run requires null counts and exit code. |
| `exit_code` | integer \| null | Observed process exit code, including negative signal codes if used; null when no exit was observed. |
| `collected` | integer \| null | Measured number of collected test cases; null if unavailable. |
| `passed` | integer \| null | Measured number of passed cases; null if unavailable. |
| `failed` | integer \| null | Measured number of assertion-failed cases; null if unavailable. |
| `errors` | integer \| null | Measured collection/setup/teardown errors in the test report; not API or tool error counts. |
| `skipped` | integer \| null | Measured skipped cases; null if unavailable. |
| `xfailed` | integer \| null | Measured expected failures; null if unavailable. |
| `xpassed` | integer \| null | Measured unexpected passes; null if unavailable. |
| `duration_seconds` | number \| null | Measured elapsed time for this test invocation; null if unavailable. |
| `report` | artifact \| null | Retained machine-readable or textual test output; preserve evidence of failure. |

## tokens

Reported token usage covering all inference calls for the attempt, including retries and auxiliary calls; no token estimates.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `source` | enum: provider_reported, opencode_reported, mixed, null | Source of observed usage counters. opencode_reported means relayed/reported usage, never a local estimate. |
| `coverage` | enum: complete, partial, null | Whether all attempt inference calls have usage evidence; null when coverage is unknown. |
| `input_tokens` | integer \| null | Complete-attempt input count as reported; null if incomplete or missing. |
| `output_tokens` | integer \| null | Complete-attempt output count as reported; null if incomplete or missing. |
| `total_tokens` | integer \| null | Complete-attempt total as reported; never fill in an unreported total by assuming input/output accounting. |
| `cache_read_tokens` | integer \| null | Complete-attempt cache-read tokens if separately reported; may overlap input tokens. |
| `cache_write_tokens` | integer \| null | Complete-attempt cache-write tokens if separately reported; may overlap input tokens. |
| `reasoning_tokens` | integer \| null | Complete-attempt reasoning tokens if separately reported; may overlap output tokens. |
| `evidence` | array<artifact> \| null | Usage reports/request records with accounting semantics and retry coverage; [] only for verified no inference calls. |

## duration

Measured durations in seconds. Timeout/interruption durations are observed elapsed time, not time to solution.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `preparation_seconds` | number \| null | Preparation time measured separately from agent execution. |
| `agent_seconds` | number \| null | Agent elapsed time including provider waits, rate-limit backoff and retries within this attempt. |
| `evaluation_seconds` | number \| null | Elapsed evaluation time after the agent stops. |
| `total_seconds` | number \| null | Measured attempt elapsed time including preparation/evaluation and orchestration overhead; not an inferred sum. |
| `agent_censored` | boolean \| null | True if agent duration ended at timeout/interruption, false if observed to normal termination, null if unavailable. |

## human_intervention

An observed human action that could influence execution; post-run scoring alone is not an intervention.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `intervention_id` | string | Stable intervention identifier unique within the trial. |
| `timestamp` | string \| null | Observed UTC action timestamp. |
| `phase` | enum: preparation, during_run, post_run, null | When the intervention occurred; post_run means an action affecting a replacement or derived submission, not routine scoring. |
| `actor_id` | string \| null | Pseudonymous human actor identifier. |
| `kind` | enum: prompt_edit, clarification, code_edit, manual_retry, configuration_change, other, null | Observed intervention type; other requires explanation in description. |
| `description` | string \| null | What the human changed or supplied and its effect, grounded in evidence. |
| `evidence` | array<artifact> \| null | Prompt/code diff or trace establishing this action. |

## ai_error

Human-reviewed error/hallucination annotation; suspected and confirmed claims remain distinguishable.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `error_id` | string | Annotation identifier unique within the trial. |
| `interaction_id` | string \| null | Linked interaction ID, or null if no single interaction can be identified. |
| `category` | enum: invented_api_or_dependency, false_repository_or_test_claim, misunderstood_requirement, regression, unsafe_action, inadequate_tests, unsupported_sovereignty_claim, other, null | Evidence-based category; other requires explanation in description. |
| `description` | string \| null | Specific claim/action and why it is erroneous; a failed hypothesis is not automatically a hallucination. |
| `assessment` | enum: confirmed, suspected, disputed, null | Human assessment status; null if unreviewed. |
| `reviewer_id` | string \| null | Pseudonymous reviewer identifier. |
| `evidence` | array<artifact> \| null | Response, diff or test evidence supporting or disputing this annotation. |

## tool_failure

Observed OpenCode/tool failure, separate from an ordinary failing benchmark test.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `failure_id` | string | Failure identifier unique within the trial. |
| `interaction_id` | string \| null | Associated interaction ID, if known. |
| `timestamp` | string \| null | Observed UTC failure timestamp. |
| `tool_name` | string \| null | Exact failing tool name as observed. |
| `invocation_id` | string \| null | Tool invocation ID as recorded. |
| `message` | string \| null | Sanitized observed failure message; never a guessed diagnosis. |
| `exit_code` | integer \| null | Observed tool process exit code, if applicable. |
| `evidence` | array<artifact> \| null | Trace establishing the failure and its context. |

## api_error

One failed API request, including retries as distinct events. A 429 can also have a linked rate-limit event.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `error_id` | string | API error identifier unique within the trial. |
| `interaction_id` | string \| null | Associated interaction ID; auxiliary calls may have no interaction. |
| `timestamp` | string \| null | Observed UTC error timestamp. |
| `request_id` | string \| null | Provider/transport request identifier; null if not exposed. |
| `http_status` | integer \| null | Observed HTTP error status; null for transport failures without a response. |
| `code` | string \| null | Exact provider/transport error code, if supplied. |
| `message` | string \| null | Sanitized actual error message. |
| `retryable` | boolean \| null | Recoverability according to the frozen retry policy, not an inferred eventual success. |
| `retry_after_seconds` | number \| null | Observed numeric Retry-After or equivalent hint; null if absent or not interpretable. |
| `evidence` | array<artifact> \| null | Sanitized error/response evidence without credentials. |

## rate_limit

Observed throttling/quota event. Never infer quota values from generic error wording.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `event_id` | string | Rate-limit event identifier unique within the trial. |
| `timestamp` | string \| null | Observed UTC event timestamp. |
| `request_id` | string \| null | Request identifier, if supplied. |
| `api_error_id` | string \| null | Linked API error ID for the same event, if captured; avoids double-counting 429 events. |
| `unit` | enum: requests, tokens, null | Quota unit explicitly reported; null when unknown. |
| `limit` | number \| null | Non-negative limit explicitly reported for the reported quota window/unit; null when absent. |
| `remaining` | number \| null | Non-negative remaining quota explicitly reported; null when absent. |
| `window_seconds` | number \| null | Quota-window length explicitly reported in seconds; null when absent. |
| `reset_at` | string \| null | Explicit UTC reset instant or unambiguous conversion of a reported timestamp; null otherwise. |
| `retry_after_seconds` | number \| null | Observed retry delay hint; null when absent. |
| `wait_seconds` | number \| null | Actual measured delay imposed by the client; not the requested retry delay. |
| `evidence` | array<artifact> \| null | Sanitized headers or throttling event evidence. |

## attempt

One execution attempt. Restarts have new IDs; transport retries remain within the same attempt.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `attempt_id` | string | Stable unique execution ID, retained even if the attempt failed. |
| `attempt_number` | integer | One-based order within the scheduled trial; 1 is the primary first-attempt result. |
| `retry_of_attempt_id` | string \| null | Previous failed attempt ID when this is a whole-run replacement; null for the first attempt. |
| `started_at` | string \| null | Observed UTC start of attempt preparation. |
| `finished_at` | string \| null | Observed UTC end of attempt, including evaluation if performed. |
| `capture_status` | enum: complete, partial, unavailable, null | Completeness of execution-event capture; null if not assessed. Completeness does not imply every provider measurement is exposed. |
| `termination_reason` | enum: completed, budget_exhausted, provider_failure, opencode_or_tool_failure, harness_or_evaluator_failure, invalid_task, protocol_violation, interrupted, null | Observed reason execution ended; completed does not imply functional success. |
| `functional_success` | boolean \| null | External task contract outcome: true/false only when evaluation supports it; null if unavailable, unrun or inapplicable. |
| `git` | git | Git/input provenance specific to this attempt. |
| `agents_md` | agents_md | Observed instruction state before and after this attempt. |
| `patch` | artifact \| null | Final frozen unified diff against the declared starting snapshot; known no change uses empty text. Include generated/untracked changes, not just tracked git diff. |
| `interaction_count` | integer \| null | Measured number of submitted user prompts/native commands, not model messages or tool calls; null when incomplete. |
| `interactions` | array<interaction> \| null | Ordered prompt journal; [] only for verified zero interactions. Partial journals require partial capture status. |
| `public_tests` | array<test_run> \| null | Recorded public test invocations before/during/after execution; [] only when verified none ran. |
| `hidden_tests` | array<hidden_test_run> \| null | Evaluator-only oracle invocations after stopping the agent; [] for verified none. Never copy tests/reports into the agent workspace. |
| `human_intervention_count` | integer \| null | Measured count of execution-influencing human actions; post-run review decisions alone are excluded. |
| `human_interventions` | array<human_intervention> \| null | Observed interventions; [] only when absence was verified. |
| `ai_errors` | array<ai_error> \| null | Evidence-backed error annotations; [] only after completed review finds none, null if unreviewed/unavailable. |
| `tool_failures` | array<tool_failure> \| null | Observed tool failure events; [] only for verified none. |
| `api_errors` | array<api_error> \| null | Observed failed API request events; no silent omission of transport retries. |
| `rate_limits` | array<rate_limit> \| null | Observed rate-limit events and quota metadata; [] only for verified none. |
| `api_request_count` | integer \| null | Actual inference HTTP/transport request attempts, including retries and auxiliary inference; null when unmeasured. |
| `duration` | duration | Measured phase durations and censoring. |
| `tokens` | tokens \| null | Measured/reported token counts. Entire object is null if no reliable usage evidence exists. |
| `trace` | artifact \| null | Full retained execution-event transcript; may be private or redacted for publication. |

## missing_measurement

Explicit explanation of unavailable, inapplicable or withheld evidence.

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `field` | string | JSON Pointer to the affected field in this result, for example /attempts/0/tokens. |
| `reason` | enum: not_exposed, not_captured, not_run, not_applicable, withheld, partial_capture, unknown | Observed reason the field is null; unknown if the reason itself is not established. |
| `details` | string \| null | Additional evidenced explanation; null if none is known. |

## Hidden-test specialization

`hidden_test_run` uses all `test_run` fields and additionally requires
`phase: evaluation`. Public runs can use baseline, agent or evaluation phase.
The distinction is enforced by the schema, not left to a collector default.

## Validation boundaries and versioning

The schema validates required fields, nullability, enums, non-negative counts,
Git/SHA formats, UTC timestamp shape, review justification, hidden-test phase,
not-run counts, and incomplete-coverage token nulls. Enable date-time format
checking with a validator that supports it to check calendar validity as well.
It cannot establish factual truth, infer measurements, prove runtime isolation,
or check cross-record equality/arithmetic. Future ingestion must separately:

1. Recompute available prompt/artifact/snapshot hashes using their declared byte
   conventions; verify task, prompt and experiment versions against manifests.
2. Require unique trial/attempt/interaction/event IDs, chronological attempt order,
   consistent retry links and valid references to interactions/API errors.
3. Check known attempt/event totals against complete capture. Do not set totals to
   partial list lengths. A test's report counters may overlap on teardown errors;
   interpret the actual framework report rather than impose a false sum rule.
4. Validate timestamp order, evidence for verdicts/identity/token accounting and
   publication permissions. A configured model ID is not proof of actual routing.
5. Enforce frozen provider/model settings, native command semantics, the human
   intervention policy and the agent/evaluator boundary independently of JSON.

Schema version `1.0.0` freezes field meanings; changing meaning or structure needs
an explicit new version and documented migration. This stage adds no ingestion,
collection, scoring or provider configuration. Null-heavy interrupted/failed
records remain valid; reports must show their missingness and cannot quietly
exclude them.
