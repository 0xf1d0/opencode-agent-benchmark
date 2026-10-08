# Repository Guidelines

## Scope and Boundaries

OpenCode is the system under evaluation: results describe OpenCode, model,
provider and fixed environment together. Codex maintains infrastructure only.
Never use Codex as a contestant, solve tasks, generate expected patches, adapt
prompts to outputs, repair submissions or replace human qualitative review.
Implement Level 1 only; Level 2 and Level 3 remain design proposals.

## Project Structure

- `benchmark/toy/fixture/`: immutable unsolved `toolbox.py` and source public tests.
- `benchmark/toy/oracle/`: evaluator-only checks; never copy into agent workspaces.
- `benchmark/toy/prompts/`: exact UTF-8 requests, versions, hashes and TP provenance.
- `providers/`: secret-free configurations, candidate metadata and owner-supplied
  catalog snapshots. Albert model IDs must be canonical snapshot `id` values.
- `scripts/`: offline workspace preparation, catalog validation and runtime locks.
- `schemas/` and `docs/`: data contracts, field references and reproduction guidance.
- `tests/`: deterministic infrastructure checks; `.github/workflows/` runs them.
- `references/tp/`: provenance notes; the PDF/archive remain local-only.

Generated workspaces live outside this repository, under the system temporary
folder by default. Their allowlist is fixture files, selected `opencode.json` and
isolated Git baseline. Never inject this root guide, oracle, catalogs, prompt
metadata or evaluator material into them. Directory separation is not a sandbox.

## Development and Validation

Use Python with four-space indentation, descriptive snake_case names and standard
library infrastructure where practical. No formatter, linter or coverage threshold
is configured. Preserve French prompt meaning and exact bytes.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
git diff --check
```

The validation suite checks the intentional public baseline: two passes and one
space-handling failure. Do not fix that fixture or run recursive oracle collection.
Prompt byte changes require updated hashes, provenance and prompt-set version.

## Authentication and Contributions

Never inspect credentials, key-bearing environment variables or OpenCode private
account/storage files. Authentication is external OpenCode-managed persistent
state; provider IDs stay `nvidia`, `mistral`, `albert`, `aristote`. No authenticated
calls, scored campaigns or sandbox implementation are authorized in this phase.

History uses concise subjects such as `Implement controlled toy benchmark`;
prefer imperative subjects. PRs describe purpose, files, validation and evidence
limits. Preserve TP/source hashes; redistribution rights are unresolved.
