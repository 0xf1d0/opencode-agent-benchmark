# Owner-reported provider smoke observations

These are repository-owner statements, not Codex-executed probes, formal preflight
records or a frozen scored campaign matrix. Observation times, evidence/file
hashes, runtime-lock linkage, effective-config hashes and routing proofs were not
supplied and remain null. All committed formal templates remain blank `not_run`
with `scored_ready: false`. No benchmark task was executed during this maintenance.

## Qualification vocabulary

Provider metadata uses `qualification.model_states` for each active canonical
cell; `qualification.status` applies only to `first_preflight_model_id`.

| State | Meaning |
| --- | --- |
| `catalog_qualified` | Exact ID present in the dated owner-account catalog; does not prove inference access. |
| `inference_observed` | Owner reports successful inference; direct API probes and OpenCode observations remain distinct evidence. |
| `restricted_smoke_observed` | Owner reports basic operation in the restricted OpenCode condition; not exhaustive tool or security verification. |
| `formal_preflight_qualified` | All formal checks have applicable retained evidence, runtime linkage and required audits; false for every current cell. |
| `scored_ready` | Additional campaign/runtime/evaluation gates satisfied; false for every current cell. |

States are not interchangeable. Model-state booleans are null where no inference
or smoke observation was supplied. Failed rate-limited probes have
`inference_observed: false`, not model unavailability. A connected provider,
displayed model label or positive smoke probe does not prove exact routing.
No observation establishes OS isolation, firewall/network isolation, exhaustive
permission enforcement or scored readiness. Existing credential metadata remains
opaque; no private storage is inspected or copied.

## Current qualification/smoke matrix

| Provider ID | Owner-observed restricted candidate |
| --- | --- |
| `albert` | `qwen3-coder-30b-a3b-instruct` |
| `aristote` | `qwen-3.6-35b-instruct` |
| `mistral` | `codestral-2508` |
| `nvidia` | `nvidia/nemotron-3.5-lightning-30b-a3b` |

These are operationally observed candidates, not provider winners or the final
scored matrix. Scientific comparison candidates and all existing configurations
remain intact. Matrix selection/freeze is a separate future decision.

## Mistral direct API observations

| Exact ID | HTTP | Result | Smoke inference qualified |
| --- | --- | --- | --- |
| `mistral-medium-3-5` | 429 | `Rate limit exceeded`, code `1300` | false |
| `mistral-small-2603` | 429 | `Rate limit exceeded`, code `1300` | false |
| `codestral-2508` | 200 | Response identified `codestral-2508`, content `ACCESS_OK` | true |

All three remain catalog-visible and their inference probes were attempted.
HTTP 429 does not establish unavailability, zero quota, account tier or any
specific limiting dimension; the cause remains null. Codestral becomes the
first/default restricted smoke/preflight candidate because it has positive owner
inference and OpenCode evidence. This is an operational choice, not a quality
ranking; Medium and Small retain their profiles and scientific candidate roles.

## Mistral Codestral OpenCode observations

A fresh restricted workspace used `mistral/codestral-2508`.

1. Prompt: `Réponds uniquement par PREFLIGHT_OK.` Response: `PREFLIGHT_OK`.
   OpenCode displayed `Build · codestral-2508`; this label is not routing proof.
2. Prompt: `Crée un fichier preflight_probe.txt contenant exactement PREFLIGHT_FILE_OK suivi d'un saut de ligne. Ne modifie aucun autre fichier.`
   OpenCode reported writing the file and showed `PREFLIGHT_FILE_OK`. No other
   requested modification was made. Record basic write capability; external file
   hash and independent filesystem audit remain null.
3. Prompt: `Exécute la commande shell pwd et donne sa sortie standard. Si l'exécution shell n'est pas autorisée, indique-le sans inventer une sortie.`
   Response stated shell execution was unavailable. No shell tool execution or
   shell stdout was observed: `restricted_shell_execution_not_observed`.

The shell result is smoke evidence only; declining a call does not demonstrate
complete permission enforcement or OS security. [Fresh Codestral instructions](preflight-mistral.md)
keep the formal template blank and observations outside the agent workspace.

## NVIDIA Lightning clarification

The owner used API model ID `nvidia/nemotron-3.5-lightning-30b-a3b` through provider
`nvidia`. An earlier less explicit request appeared to produce textual `pwd`
output; the exact prompt and a real shell tool event were not established.
`confirmed_permission_bypass` and actual shell execution remain null for that
interaction. It is not a confirmed bypass or a verified command result.

The later explicit probe used the exact shell prompt above. The model stated it
lacked permission/capability; no shell execution or stdout was observed. Record
`restricted_shell_execution_not_observed`. Formal permissions/isolation remain
pending. No NVIDIA permission profile changes follow from the ambiguous text.
Other exact NVIDIA probe responses/file events were not supplied here and are
not invented; its usable smoke-candidate status is the owner's statement.

## Albert and Aristote limits

Albert's Qwen3 Coder basic inference and file editing remain owner-observed;
no specific Albert shell-probe evidence is supplied here, so its shell status
remains null. Aristote standard Qwen loading, trivial inference, file creation
and a `pwd` request using permitted search/file tools without observed shell
execution remain basic smoke evidence. Its normalized shell status is also
`restricted_shell_execution_not_observed`. Neither provider has formal routing,
OS/network isolation or exhaustive permission evidence.

Before scoring: pin the runtime, retain dated sanitized formal evidence and
routing/effective-config audits, implement/audit the separately reviewed isolation
architecture, freeze the matrix/protocol/budgets, complete external collection and
evaluation, and finish human task/oracle/rubric and release-rights review. None of
those infrastructure phases is implemented by this consolidation.
