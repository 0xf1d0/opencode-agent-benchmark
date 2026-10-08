# Offline OpenCode campaign locks

`scripts/runtime_lock.py` prepares and validates versioned provenance. It never
launches OpenCode, downloads a release, reads credential state or calls a provider.
An exact release must be selected by the owner: no release is guessed or silently
upgraded. Current installed OpenCode version is **null/unobserved** in repository
metadata. An earlier version probe could not write its log under the filesystem
policy; it did not establish a version. This phase does not re-probe private state.

## Workflow

Install validation dependencies, choose an exact release and record its checksum
from an owner-controlled artifact. The command below uses explicit placeholders;
replace them with observed values, not `latest`:

```sh
.venv/bin/python scripts/runtime_lock.py create \
  --provider albert --model qwen3-coder-30b-a3b-instruct \
  --prompt-id 01_bugfix --run-id preparation-001 --campaign-id CAMPAIGN_ID \
  --opencode-version EXACT_X.Y.Z --output /tmp/level1-runtime-lock.json
.venv/bin/python scripts/runtime_lock.py check \
  --manifest /tmp/level1-runtime-lock.json
```

Optional owner inputs are `--observed-opencode-version`,
`--opencode-artifact-sha256`, `--runtime-image` and `--sandbox-review-id`.
No corresponding binary/image is downloaded or executed. Creation refuses overwrite.
The output belongs outside the agent workspace. A bare check validates shape and
current preparation provenance, not runtime qualification. `check --for-scoring
--preflight /path/to/owner-record.json` additionally rejects dirty sources, missing
observations/audits and unqualified or mismatched cells. It does not launch a run,
attest an OS boundary or replace a frozen campaign protocol.

Schema: [`runtime-lock.schema.json`](../schemas/runtime-lock.schema.json).
All fields are required; unknown observations are null. No committed campaign
lock or scored-ready runtime is supplied. Locks are canonical indented JSON when
created; preflight hashes always cover the exact lock bytes, including whitespace.

## Canonical provider selection

All four providers have hashed owner catalogs. NVIDIA IDs contain `/`;
preparation resolves only the explicit safe-directory registry in
`providers/nvidia/metadata.json` and `scripts/nvidia_catalog.py`. It never treats
the raw API ID as a relative filesystem path. Runtime locks retain the exact
canonical ID, registered profile path/hash and NVIDIA catalog hash. Unknown or
non-selected IDs fail closed, including explicit config overrides. Current
selected profiles are restricted with the provisional 32768/4096 benchmark cap.
[Mappings and review](nvidia-review.md) document every active cell.

Task locks bind task prompts; do not use a toy prompt to manufacture linkage for
a non-task smoke preflight. See [owner Lightning instructions](preflight-nvidia.md).

## Field reference

| Field | Meaning |
| --- | --- |
| `schema_version`, `record_type` | Contract version 1.0.0 and campaign_runtime_lock preparation record. |
| `run_id`, `campaign_id`, `benchmark_level` | Declared run/campaign identities; Level 1 only. |
| `benchmark_commit`, `benchmark_dirty` | Observed source HEAD/worktree state; scoring requires committed clean inputs. |
| `opencode_version` | Owner-selected exact expected release, never a floating alias. |
| `observed_opencode_version` | Owner-reported actual runtime observation; null until supplied, must match the pin before scoring. |
| `opencode_artifact_sha256` | Owner-supplied executable/distribution checksum, null until supplied; required by offline scoring gate. |
| `autoupdate` | Always false; installation/upgrades are outside this utility. |
| `python_version`, `pytest_version`, `git_version` | Actually observed preparation versions; missing installed packages/tools remain null. |
| `operating_system` | Observed preparation OS and release. |
| `runtime_image` | Immutable execution-image digest/reference if applicable; null before selection. A mutable image tag alone is insufficient for a campaign. |
| `provider`, `model_id` | Exact registered provider/canonical model; Catalog-backed providers reject unknown, floating and non-preferred alias IDs. |
| `provider_config_path`, `provider_config_sha256` | Relative config path and SHA-256 of unchanged bytes. |
| `provider_evidence_sha256` | Exact provider metadata hash; linked remote pages are not themselves archived by this digest. |
| `catalog_snapshot_sha256` | Exact sanitized catalog bytes, null where no catalog snapshot exists. |
| `fixture_version`, `fixture_manifest_sha256` | Immutable fixture identity and exact manifest hash. |
| `prompt_set_version`, `prompt_id`, `prompt_sha256` | Frozen prompt-set identity and exact UTF-8 prompt hash. |
| `prompt_metadata_sha256` | Provenance/manifest bytes, separate from delivered text. |
| `requirements_sha256`, `requirements_resolved_sha256` | Exact direct validation pins and CI resolution-lock hashes. |
| `protocol_track` | restricted / agentic; utility currently prepares restricted only. |
| `sandbox_review_id` | Owner-approved isolation implementation audit reference, null while unimplemented. |
| `preparation_environment_only` | Always true: execution must separately record/attest equal runtime provenance. |
| `created_at` | Observed UTC preparation timestamp. |

The future collector must retain these fields with every scored result and compare
actual execution provenance; a manifest cannot prove what ran. Result schema 1.1.0
references the exact lock artifact. Catalog evidence can expire without changing
Git hashes. Owner preflight must therefore be dated and linked to the intended
campaign; no automatic freshness threshold is invented.

## CI dependencies and reproducibility limits

`requirements-dev.txt` fixes direct validation dependencies.
`requirements-ci.lock` records the complete installed resolution from Python 3.14.4;
CI installs it on Python 3.14.4. Other supported preparation Python versions may
require their own compatible lock; do not silently regenerate this one mid-campaign.
Package distribution hashes, an immutable OS image, action commit pins, the trusted
adapter and numeric resource budgets remain campaign/release work. CI is an
infrastructure check, not a scored experimental runtime. Hosted inference can drift
even with immutable local artifacts; exact output replay is not promised.
