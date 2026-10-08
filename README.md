# OpenCode Agent Benchmark

A public, reproducible benchmark under development for **OpenCode + model +
inference provider + fixed environment**. It studies coding-agent workflows,
operational reliability and deployment choices, with particular interest in French
sovereign infrastructure. It does not measure intrinsic model intelligence alone.
Codex maintains the infrastructure only and never participates in benchmark runs,
solves tasks, repairs submissions or performs qualitative grading.

## Methodology and levels

The local TP motivates initialization/`AGENTS.md` inspection, palindrome repair,
progressive specifications, generated tests, underspecified optimization/native
undo, same-prompt comparison, Git principles, prompt journals and critical review.
Immutable fixtures, hidden evaluation, repeated trials, provider matching,
structured provenance, sandboxing and statistics are benchmark extensions.
See [design](DESIGN.md), [methodology](METHODOLOGY.md) and
[reference provenance](references/tp/README.md). The TP PDF is intentionally
local-only, not distributed here; redistribution rights remain unresolved.

| Level | Scope | Status |
| --- | --- | --- |
| 1 | Controlled Python toy project | Fixtures, prompts, oracle, configs, schemas and workspace preparation implemented; runner and evaluation collection pending |
| 2 | Git workflow benchmark | Designed; not implemented |
| 3 | Tasks reconstructed from merged PRs | Designed; not implemented |

Level 1 covers a deliberately broken palindrome, three independent
`word_frequency` specification conditions, test generation, ambiguous optimization,
native undo and Celsius conversion. `/init` and guide review are separate command
conditions. Each specification variant starts from the same declared snapshot;
it is not a sequence of progressively repaired code. The public baseline is
**2 passing tests, 1 intended failure**. There are no scored campaign results.

## Models, providers and qualification

Model comparison varies models within a provider. Provider comparison varies
inference deployments; different models introduce confounding. Same-family
comparisons are useful where supported, but do not prove identical checkpoints.

| Provider | Current candidates | Qualification |
| --- | --- | --- |
| NVIDIA Build | `z-ai/glm-5.3` | Documented identifier; runtime unqualified |
| Mistral AI direct | `mistral-medium-3-5`, `mistral-small-2603`, `codestral-2508` | Owner catalog qualified; 46 records clustered; runtime preflight unperformed |
| Albert | Qwen3 Coder first, GPT OSS, DeepSeek V4 Flash, Mistral Small 3.2 | Owner catalog qualified; Qwen3 Coder basic inference/editing owner-observed; formal qualification incomplete |
| Aristote | Standard/reasoning-high Qwen 3.6, Qwen 3.8, Mistral Small 3.2/4 | Owner catalog qualified; basic restricted inference/file creation owner-observed; formal qualification incomplete |

NVIDIA/Mistral GLM 5.3 is **not currently executable** for the owner account:
`zai-glm-5-3` is absent from its Mistral snapshot. Mistral/Aristote Small 4 is a
supported **model-family-only** pairing; no served equivalence is established.
Albert no longer has an active Mistral Medium configuration. Albert/Aristote Mistral Small 3.2 is another
**model-family-only** candidate pairing: catalog names do not establish identical
checkpoints. There is no fixed Mistral Small 3.2 ID in the direct catalog, so this
is not a three-provider comparison. Aristote's `mistral-medium-latest` is floating
and not eligible as a pinned Medium 3.5 match. Albert and Aristote remain separate deployments.
French ownership, hosting, certification and retention require separate evidence;
sovereignty is not a capability score. See [provider metadata](providers/README.md).
**No provider/model cell is scored-ready.**

## Reproduce infrastructure validation

Use Python 3.10+; CI currently fixes Python 3.14.4. Dependency installation needs
package-index access; validation itself requires no provider access or credentials.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
git diff --check
```

Prepare a disposable workspace without starting OpenCode:

```sh
python scripts/create_workspace.py --benchmark toy --provider albert \
  --model qwen3-coder-30b-a3b-instruct --run-id preparation-001
python scripts/create_workspace.py --benchmark toy --provider aristote \
  --model qwen-3.6-35b-instruct --run-id aristote-preflight-001
python scripts/create_workspace.py --benchmark toy --provider mistral \
  --model mistral-medium-3-5 --run-id mistral-preflight-001
```

Only fixture code, public tests, selected config and a new Git baseline enter the
workspace. Root instructions, hidden oracle, reference materials, metadata and
credentials do not. Preparation is not runtime isolation; do not launch scored
runs on the maintainer host. Authentication remains private OpenCode-managed
persistent state, loaded for the fixed project provider ID. Never inspect or copy
its implementation-specific storage.

## Remaining work and limitations

The implemented `restricted` profiles disable shell/web tools and require external
test execution. An `agentic` track with local Python/pytest/Git is designed only;
its OS sandbox requires architecture review before implementation. See
[runtime design](docs/runtime.md) and [runtime locks](docs/runtime-pinning.md).

For an owner-only non-scored smoke observation, follow the
[manual Mistral steps](docs/preflight-mistral.md); Codex does not execute them.
Formal preflight requires selecting and pinning an exact release, reviewing the isolation
boundary and implementing/auditing the required runtime. Before scoring: complete
owner-driven per-cell qualification, freeze budgets/task manifests, implement
external collection/evaluation, review oracles/rubrics and resolve release rights.
Threats include public-task contamination, incomplete oracles, provider drift,
opaque checkpoints, finite French/Python tasks, prompt sensitivity, outages and
reviewer bias. Separate correctness, agent behavior, operational performance,
human review and deployment evidence; no arbitrary combined score is defined.
