# Repository Guidelines

## Project Structure & Module Organization

This repository is an initial scaffold for benchmarking coding-agent workflows. `references/tp/README.md` records the methodological inspiration, including bug fixes, implementation from specifications, test generation, model comparisons, and Git workflows.

There are currently no source modules, test suites, or application assets. Keep reference material under `references/`. When adding executable benchmarks, group implementation and tests clearly and document their locations and entry points.

## Build, Test, and Development Commands

No build system, dependency manifest, or automated test command is configured yet. Use these commands to inspect contributions:

- `git status --short`: review changed and untracked files.
- `git diff --check`: detect whitespace errors in tracked changes.
- `git diff`: review tracked edits before committing.

When introducing tooling, document exact installation, execution, and testing commands alongside the implementation. Avoid describing commands as supported until their configuration exists.

## Coding Style & Naming Conventions

Use descriptive filenames and concise Markdown with ATX headings (`## Section`). Keep documentation actionable and commands copyable. Preserve the meaning of the French methodology notes when editing them.

No language-specific formatter, linter, or indentation policy exists. Configure and document these conventions when introducing the first implementation language.

## Testing Guidelines

No testing framework or coverage threshold is established. New executable benchmarks should include reproducible inputs, expected outcomes, and a documented validation command. Give tests descriptive names that identify the behavior or benchmark scenario being checked.

For documentation changes, verify paths, command accuracy, and Markdown readability.

## Commit & Pull Request Guidelines

The repository has no commits yet, so there is no historical commit-message convention. Use short, imperative subjects such as `Add benchmark scenario documentation`.

Pull requests should explain the purpose, changed files, and validation performed. Link relevant issues when available. For benchmark changes, record the agent or model, scenario, execution conditions, and results needed to reproduce the comparison.

## Reference Material

`.gitignore` excludes `references/tp/TP_IA_INTRO_26_27.pdf`. Keep this local reference untracked unless the repository explicitly changes that policy.
