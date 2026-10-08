# Preparing a Level 1 workspace

[`scripts/create_workspace.py`](../scripts/create_workspace.py) prepares files and
Git history only. It does not start OpenCode, connect to an API, discover models,
install dependencies, copy authentication state or evaluate a benchmark task.
Python 3.10+ and Git on the system executable path are required.

## Usage and configuration selection

From the repository root:

```sh
python scripts/create_workspace.py \
    --benchmark toy \
    --provider nvidia \
    --model glm-5.3 \
    --run-id 001
```

This selects `providers/nvidia/opencode.json`. The current NVIDIA profile uses the
published ID `z-ai/glm-5.3`, so replace the example's short `--model glm-5.3` with
`--model z-ai/glm-5.3`; mismatches are refused. See the
[implemented provider profiles](../providers/README.md). Supply another audited
configuration explicitly when needed:

```sh
python scripts/create_workspace.py \
    --benchmark toy --provider nvidia --model z-ai/glm-5.3 --run-id 001 \
    --config /path/to/audited/opencode.json \
    --output-root /tmp/my-benchmark-workspaces
```

`--model` is the exact provider model ID, including a family prefix if applicable;
it is recorded unchanged and is not a claim about availability. Configuration
`model` must be exactly `<provider>/<model>`. Any declared `small_model` must
match it. Provider/run identifiers must be safe single path components. The same
benchmark/provider/run ID cannot be reused, even with a different model.

The config is copied byte-for-byte after validation. This first implementation
accepts strict UTF-8 JSON in OpenCode's **v1 `provider` format**; JSONC and the v2
`providers` format are rejected rather than translated speculatively. The actual
OpenCode CLI version and configuration compatibility still require preflight.

Supported configuration fields are deliberately narrow:

| Location | Allowed fields and constraints |
| --- | --- |
| Root | `$schema` (official config URL), exact `model`, matching `small_model`, `provider`, `autoupdate: false`, `share: disabled`, `compaction`, `tools`, `permission`, selected-only `enabled_providers`, empty `mcp`/`plugin`, `lsp: false`, `formatter: false` |
| `provider` | Only the selected provider; its fields are `npm`, `name`, `options`, `models` |
| Provider `npm` | `@ai-sdk/openai-compatible`, `@ai-sdk/openai`, or `@ai-sdk/mistral`; no local/package override |
| Provider `options` | `baseURL`, `apiKey`, `headers`, positive integer `timeout` and `chunkTimeout` |
| Provider `models` | Only the selected model; its fields are `name` and `limit` with positive integer `context`/`output` |
| `compaction` | Boolean `auto`/`prune` and positive integer `reserved` |
| `tools` | `task`, `webfetch`, `websearch`, `bash`, `skill`, `lsp`, each explicitly `false` if present |
| `permission` | Executable/external tools and `*` may only be denied; local read/edit/search/clarification tools may be allowed; structured read/edit rules must exactly match the audited offline profile |

Omitted optional controls are not silently invented. Runtime preflight must still
verify effective settings, isolate global configuration, and prevent auxiliary
inference fallback. Config validation here does not certify model capabilities or
prove the agent sandbox is secure.

## Credential handling

`apiKey` must contain only an unresolved `{env:VARIABLE_NAME}` reference when
present. Header values also require an environment reference; `Authorization`
may use `Bearer {env:VARIABLE_NAME}`. Only `Accept`/`Content-Type` may alternatively
contain the fixed literal `application/json`. These references are supported by
the [OpenCode config documentation](https://opencode.ai/docs/config/#env-vars).

Literal keys/tokens, credential file references, URL user/password/query/fragment,
unknown configuration fields, duplicate JSON keys and non-finite numbers are
rejected before output creation. Configuration validation errors do not print
input keys/values. Configs should still be deliberately authored and audited;
this narrow format is not a general-purpose secret scanner.

The script does not expand references, read environment credentials, copy `.env`,
`auth.json`, user configuration or databases, or inherit Git's process environment.
Workspace preparation creates no provider configurations. The separate profiles
are [documented here](../providers/README.md). Runtime credential injection belongs to a
separate isolated authentication boundary, not a file in this workspace.

## Output and visibility

Default output is under the system temporary directory:

```text
opencode-benchmark-workspaces/toy/nvidia/001/
  initial_metadata.json            preparation evidence; evaluator/harness only
  workspace/                      the only directory mountable into OpenCode
    toolbox.py
    test_toolbox.py
    opencode.json
    .git/                         independent baseline history
```

The output must be outside the benchmark repository. Existing directories, files
and symlink destinations are refused; there is no force/overwrite option. Failed
preparation removes only its newly reserved run directory. Successful output paths
are emitted as JSON to stdout. The script can be invoked from any working directory;
source/default-config paths are anchored to the script's repository.

Only the two manifest-listed fixture files are copied, never the whole fixture
directory. Oracle files, prompts, metadata, the benchmark's `AGENTS.md`, caches,
authentication files and parent Git history are excluded. The fixture is verified
against [`fixture_manifest.json`](../benchmark/toy/fixture_manifest.json) before
copying; changed content or symlinked inputs are refused. Updating a fixture means
deliberately versioning the manifest, not editing copies in place.

A new Git repository starts on `main`, with one baseline commit containing exactly
the three public files. Git templates/hooks, global/system config, inherited Git
environment variables, global attributes and automatic signing are disabled during
preparation. Baseline identity is synthetic and its canonical timestamp is
`2000-01-01T00:00:00+00:00`, allowing identical bytes to produce identical baseline
commits. This timestamp is a construction constant, not measured execution time.
The actual preparation timestamp is recorded in metadata.

Mount **only `workspace/`** into a runtime without access to its parents or the
benchmark repository. Directory separation and Git initialization do not restrict
host filesystem access, global OpenCode settings or network egress. Runtime
sandboxing and provider preflight are separate gates before scored execution;
this script intentionally does not launch a benchmark run.

## Initial metadata

`initial_metadata.json` is a preparation record, **not** an executed result under
`schemas/result.schema.json`. Its fields are:

| Field | Meaning |
| --- | --- |
| `schema_version`, `record_type` | Version `1`; record type `workspace_initialization` |
| `created_at` | Observed UTC time preparation completed |
| `benchmark`, `provider`, `model_id`, `run_id` | Exact selected benchmark/deployment/model/run identifiers |
| `model_family`, `opencode_version` | `null`: neither family nor CLI version is observed by preparation |
| `workspace` | Relative workspace directory, always `workspace` |
| `fixture_version`, `fixture_manifest_sha256` | Immutable fixture version and source manifest digest |
| `config_format`, `config_sha256` | Validated `opencode_v1` format and exact copied config digest |
| `files` | Mapping of the three copied filenames to their byte SHA-256 digests |
| `task_snapshot_sha256`, `snapshot_hash_method` | Digest of compact, sorted-key UTF-8 JSON of `files`; explicitly stated hashing method |
| `benchmark_commit`, `benchmark_dirty` | Observed full source commit and dirty status; `null` if unavailable |
| `baseline_commit`, `git_version` | Observed new baseline commit and Git version |
| `agents_md` | `[]`: no guide is placed in the initial workspace; initialization is a benchmark task |

No test, token, timing-of-agent or response result is fabricated. Metadata stays
outside the agent-visible repository, with owner-only permissions.

## Validation

Infrastructure tests need only the Python standard library and Git:

```sh
python -m unittest discover -s tests -p test_create_workspace.py -v
```

They check byte-preserving copies, oracle/credential exclusion, inherited Git state,
the clean isolated baseline, repeatable commit hashes, traversal/symlink rejection,
configuration rejection, failure cleanup and overwrite refusal. They create only
temporary synthetic configurations and never contact providers or solve tasks.
