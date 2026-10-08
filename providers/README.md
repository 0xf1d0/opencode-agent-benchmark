# Provider profiles

These versioned OpenCode v1 JSON profiles implement the benchmark's provider
selection and agent permission policy. No secrets, auth databases or connection
files are stored here. Profiles preserve the user's existing `/connect` credentials
by omitting `apiKey`. All four saved connection IDs must match the lowercase IDs
below; no credential store was inspected to verify them.

## Selected identifiers and evidence

Reviewed on 2026-10-07. Documentation verification is separate from authenticated
availability, tool-calling preflight and exact served-checkpoint verification.

| Provider ID | Default exact API identifier | Evidence and verification limits |
| --- | --- | --- |
| `nvidia` | `z-ai/glm-5.3` | [NVIDIA Build's model example](https://build.nvidia.com/z-ai/glm-5-3?section=deploy) publishes this identifier and the hosted API endpoint. Served checkpoint revision remains unknown. |
| `mistral` | `zai-glm-5-3` | [Mistral's GLM 5.3 card](https://docs.mistral.ai/models/zai-glm-5-3) publishes this identifier. This is a third-party model served through Mistral direct. Exact serving equivalence with NVIDIA is unverified. |
| `albert` | `Mistral-Medium-3.5-128B` | A search excerpt from the [government Albert coding repository](https://github.com/etalab-ia/albert-code) lists this identifier. Its rendered page did not expose the listing; the [official authenticated catalog](https://albert.api.etalab.gouv.fr/reference) was not queried. **Current identifier/catalog availability is unverified.** |
| `aristote` | `qwen-3.6-35b-instruct` | The user-supplied official **Détails techniques** excerpt documents this identifier and recommends it as the starting model. Its publication date/exact page URL and current availability are **unverified**. The supplied excerpt remains the source; no repeat retrieval was performed after the user's clarification. |

Do not shorten NVIDIA's identifier to `glm-5.3`: the published request ID includes
`z-ai/`. The default NVIDIA/Mistral pair supports a **model-family-only** comparison
of GLM 5.3, not an identical-checkpoint claim. Hosted weights revision and actual
quantization remain null for every profile.

`mistral/opencode.medium.json` selects `mistral-medium-3-5`, published by
[Mistral's Medium 3.5 card](https://docs.mistral.ai/models/mistral-medium-3-5-26-04).
It is a candidate family comparison with Albert; neither the same weights nor
Albert's current account access is established. No alias is silently resolved to
a dated checkpoint. No currently retired Small 3.2 direct profile is promoted
from the TP-era model list.

## Authentication

Default `opencode.json` files contain no `apiKey` or authorization headers. Existing
`/connect` state supplies authentication for `nvidia`, `mistral`, `albert` and
`aristote`. [OpenCode documents NVIDIA's native connection](https://opencode.ai/docs/providers/#nvidia);
its [provider source](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/provider/provider.ts)
also loads saved API connections for configured providers and uses that key when
`options.apiKey` is absent. Mistral's native SDK/provider is registered in the
[OpenCode model registry](https://github.com/anomalyco/models.dev/blob/dev/providers/mistral/provider.toml).
This is source evidence, not a live test of the user's installed version.

For **custom providers without a usable saved connection**, use the optional
`albert/opencode.env.json` or `aristote/opencode.env.json` file. They contain only
`{env:ALBERT_API_KEY}` and `{env:ARISTOTE_API_KEY}` references. OpenCode performs
runtime substitution; the workspace creator never expands or reads those values.
Do not use these variants for the existing connections unless deliberately switching
authentication: an unset variable can override a saved key with an empty value.

All credentials stay outside Git, generated workspaces and benchmark metadata.
Do not copy `auth.json`, the OpenCode database, `.env` or an entire user config
directory into an agent mount. Reusing a saved connection requires a separate
isolated authentication boundary, not exposing the user's home to the agent.
No inference or authenticated catalog call was made during this implementation.

## Workspace preparation

For example:

```sh
python scripts/create_workspace.py \
    --benchmark toy --provider nvidia --model z-ai/glm-5.3 --run-id 001

python scripts/create_workspace.py \
    --benchmark toy --provider mistral --model zai-glm-5-3 --run-id 001

python scripts/create_workspace.py \
    --benchmark toy --provider albert --model Mistral-Medium-3.5-128B --run-id 001

python scripts/create_workspace.py \
    --benchmark toy --provider aristote --model qwen-3.6-35b-instruct --run-id 001
```

Explicit alternatives use `--config`, for example
`--provider mistral --model mistral-medium-3-5 --config providers/mistral/opencode.medium.json`.
Only the selected config enters the workspace, never this README or provider
metadata. Preparing an unverified candidate does not make it eligible for scoring.

## Web and executable-tool policy

Every profile disables `webfetch`, `websearch`, shell (`bash`), delegation (`task`),
skills and LSP tools at both tool and permission levels. Unknown tools default to
`deny`. MCP, plugins, LSP servers, automatic formatters, updates and sharing are
disabled. Only the selected provider is enabled; auxiliary inference selects the
same model, and automatic compaction is disabled.

File read/search/edit and clarification remain available within the task mount.
Agent edits to `opencode.json`, `opencode.jsonc`, `.opencode/`, `.git/`, auth and
credential files are denied. This prevents ordinary agent edits from re-enabling
network/executable tools or installing hooks. These are explicit benchmark
extensions, not permissions prescribed by the TP.

Shell is disabled because a command-name blacklist cannot stop Python/generated
tests from fetching URLs. Consequently **the agent cannot launch pytest or Git
commands through its shell tool in this profile**. Public tests must run in a
deterministic external harness; hidden tests remain evaluator-only. No harness
is implemented by this change. Native initialization/undo compatibility still
needs a pinned-runtime check. Any future shell-enabled profile requires verified
OS network isolation and separate versioned protocol reporting.

OpenCode [merges configuration sources](https://opencode.ai/docs/config/#locations).
Empty plugin/MCP lists alone do not prove inherited settings are absent. Before
scored execution, isolate configuration and credentials, audit the effective
settings, test deny behavior on the pinned version, and enforce egress restrictions
allowing inference transport while denying agent web access. These profiles are
not an OS firewall; metadata records `scored_ready: false` and unperformed checks
as null. The installed version could not be measured because its version command
attempted to write a read-only log; no compatibility value was guessed.

## Limits and metadata

The common local limits of **32,768 context / 4,096 output tokens** are provisional
benchmark configuration caps. They are not measurements or asserted service
maxima. Aristote's supplied documentation describes those local values for its
Reasoning High/Mistral configurations and says service ceilings require DISI
confirmation; applying a common cap here is our explicit experimental extension.

Each `metadata.json` records exact selected IDs, sources/source kinds, verification
status, unknown checkpoint/quantization/access measurements, authentication mode,
config SHA-256 hashes and local-budget/network policy. `model-family-only` means
served weight identity is not established even when the API request ID is documented.
`unverified_current_catalog` means a candidate ID is evidenced but current
deployment membership has not been established. Null means unmeasured, never zero
or inferred success. Refresh provenance and hashes whenever a profile changes.

Validate offline integration without credentials or model calls:

```sh
python -m unittest discover -s tests -v
```
