# Owner-driven provider/model qualification

This is a data contract and unperformed example, not a preflight runner.
Codex makes no authenticated calls and never discovers or inspects credentials.
The first proposed cell is `albert/qwen3-coder-30b-a3b-instruct` in the `restricted`
track. [`runtime/preflight.albert.example.json`](../runtime/preflight.albert.example.json)
records all checks as `not_run`, measurements null and `scored_ready: false`.

Authentication is external OpenCode-managed persistent state. Project provider
IDs remain fixed. Loading a custom provider definition may be necessary for it to
appear in `/connect`; a connected icon does not prove inference/tool compatibility.
An authenticated catalog proves account availability only at its retrieval date.

Schema: [`preflight.schema.json`](../schemas/preflight.schema.json).

## Fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Preflight contract version 1.0.0. |
| `provider`, `model_id`, `protocol_track` | Exact canonical cell and restricted/agentic policy. Never use Albert aliases. |
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
