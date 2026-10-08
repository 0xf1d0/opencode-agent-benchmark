# Owner-driven provider/model qualification

This is a data contract with unperformed templates, not a preflight runner.
Codex makes no authenticated calls and never discovers or inspects credentials.
The first proposed cell is `albert/qwen3-coder-30b-a3b-instruct` in the `restricted`
track. [`runtime/preflight.albert.example.json`](../runtime/preflight.albert.example.json)
records all checks as `not_run`, measurements null and `scored_ready: false`.
The owner separately reports successful Albert Qwen3 Coder basic inference and
file editing in the restricted condition. Formal runtime pins, dated sanitized
evidence and the remaining checks are incomplete. Provider metadata records the
statement as an owner observation; the blank template is not a retroactive report.

The first Aristote cell is `aristote/qwen-3.6-35b-instruct`, also `restricted`.
[Its template](../runtime/preflight.aristote.example.json) leaves every check
`not_run` and `scored_ready: false`. The exact owner-authenticated Aristote catalog
is now archived and hashed in provider metadata; no Aristote runtime checks have
been performed by Codex. The owner has now observed Aristote loading, trivial inference
and file creation, plus a `pwd` request that produced no shell execution/stdout and
used permitted file/search tools. This is recorded separately in provider metadata,
with missing times/hashes/linkage/routing proof null, not formal passed checks.

The first Mistral cell is `mistral/mistral-medium-3-5`, `restricted`.
[Its unperformed template](../runtime/preflight.mistral.example.json) keeps every
check `not_run` and `scored_ready: false`. Follow the
[manual owner instructions](preflight-mistral.md) for a basic non-scored observation.
All three catalog-backed providers remain short of full scored qualification.

Authentication is external OpenCode-managed persistent state. Project provider
IDs remain fixed. Loading a custom provider definition may be necessary for it to
appear in `/connect`; a connected icon does not prove inference/tool compatibility.
An authenticated catalog proves account availability only at its retrieval date.

Schema: [`preflight.schema.json`](../schemas/preflight.schema.json).

## Fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Preflight contract version 1.0.0. |
| `provider`, `model_id`, `protocol_track` | Exact canonical cell and restricted/agentic policy. Use exact preferred IDs; never normalize IDs or select floating/alternative aliases. |
| `runtime_lock_sha256` | SHA-256 of exact tested runtime-lock bytes, null before a lock is selected. |
| `performed_by` | repository_owner after human qualification, null before execution. |
| `authentication.mode` | Always opencode_managed_persistent_credential. |
| `authentication.provider_id` | Exact project provider ID, matching the cell. |
| `authentication.credential_storage_location` | Always null; never discover or record it. |
| `authentication.credential_storage_location_verified` | Always false; storage implementation is outside reproducibility. |
| `authentication.credential_present_usable` | Owner-observed usable authentication; null before an applicable probe. |
| `checks` | Nine separate observations, listed below. |
| `checks.<name>.status` | not_run / passed / failed / unverified. |
| `checks.<name>.observed_at` | UTC observation time; null before execution. |
| `checks.<name>.evidence_sha256` | Hash of sanitized retained evidence; null before execution. Passed checks require evidence and time. |
| `checks.<name>.notes` | Factual observations and limitations, null if unavailable. |
| `os_boundary_verified` | Owner audit of filesystem/process/credential/network isolation, null until tested. |
| `effective_configuration_sha256` | Sanitized effective settings hash, including inherited state; null until audited. |
| `observed_provider`, `observed_model_id` | Actual routing observations, null when unavailable. |
| `scored_ready` | False until all runtime, identity and isolation gates pass; not implied by authentication or catalog presence. |
| `notes` | Qualification limits and human review, null when unavailable. |

## Independent checks

| Check name | Required observation |
| --- | --- |
| `project_configuration_loads` | Pinned OpenCode accepts the selected v1 config unchanged. |
| `provider_visible` | Exact project-defined provider appears. |
| `canonical_model_visible` | Exact canonical model appears. |
| `inference_succeeds` | Owner observes successful inference without a benchmark task. |
| `trivial_conversation_succeeds` | Fixed non-scored trivial exchange completes. |
| `required_tool_calling_works` | Frozen synthetic tool round trip works; no toy implementation or expected patch. |
| `permissions_enforced` | Track-specific deny/allow behavior and protected config work. |
| `context_output_configuration_accepted` | Configured caps are accepted; this does not measure server ceilings. |
| `no_unintended_fallback` | All inference routes, including auxiliary traffic, use the selected provider/canonical ID. |

A future qualification protocol must freeze exact trivial prompts/tool fixtures,
acceptance observations, retry rules and evidence redaction before execution.
They are not task prompts and are not implemented here. Every check is independent:
failed tool calling must not be hidden by a successful conversation. Partial checks
remain visible; missing evidence is null. No outcome-dependent model substitution.

The schema enforces a minimum evidence shape for `scored_ready: true`; the offline
lock checker also checks cell/auth/routing identity and exact lock linkage. Neither
can prove the truth of owner observations. Scored campaigns additionally require
approved isolation, task/rubric review, collection/evaluation, budgets, schedule,
release rights and a frozen protocol. The current repository satisfies none of
those gates merely by containing this schema.
