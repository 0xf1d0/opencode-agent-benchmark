# Level 1: controlled toy workflow

This level follows TP §3.2 (PDF pp. 4–5): baseline tests, initialization and guide
review, palindrome repair, implementation from specification, generated tests,
an underspecified optimization and undo, then a same-prompt model comparison.
The initial `toolbox.py` is exactly the fixture supplied by the benchmark owner:
the missing space normalization is intentional; both other functions remain
unimplemented. Codex has not executed or solved these tasks.

## Provenance and verified baseline

The owner supplied `references/tp/TutoOpenCode.zip`. Its SHA-256 is
`2ac1cf75d503e358b913fa7b3942d2272d4e5d9c1034dd8624a9ec37dc459558`.
`fixture/test_toolbox.py` is a byte-for-byte copy of the archive member
`bac-a-sable/test_toolbox.py`, with SHA-256
`14e828125a085783d6a0d8e149b45a9bf59222348be748c418c7c47bfc094789`.
The fixture implementation matches the owner's requested code; the archive
implementation differs only by an explanatory comment beside the intentional bug.
The archive's README also documents the workflow and native `/init` and `/undo`
commands. Oracle tests are original benchmark extensions, not source tests.

Baseline verified with Python 3.14.4 and pytest 8.4.2: **2 passed, 1 failed**.
`test_is_palindrome_with_spaces` fails on `"un roc si biscornu"` as intended;
`test_is_palindrome_simple` and `test_is_palindrome_false` pass. No task solution
was created to validate this baseline. Source redistribution rights remain a
public-release gate as described in `METHODOLOGY.md`.

## Agent-visible workspace

Only `fixture/toolbox.py` and `fixture/test_toolbox.py` are initial workspace
inputs. Create a fresh directory outside the benchmark repository and copy
these two files explicitly. Never copy
`benchmark/toy/` recursively, the repository root, or `oracle/` into a workspace.
Never start OpenCode in the benchmark repository. For actual runs, mount only
the selected workspace into an isolated runtime, with no access to the benchmark
repository, evaluator or oracle through parent directories, Git objects or tools.
Directory separation alone is not a security boundary; runtime enforcement is
not implemented in this fixture-only stage. No OpenCode run should start until
that isolation exists.

## Workflow and prompts

1. Run the public tests and inspect the intentional failing palindrome case.
2. Invoke the initialization command from `prompts/00_init.txt` through the pinned
   OpenCode command interface; inspect generated `AGENTS.md` for factual accuracy.
3. Deliver `01_fix_palindrome.txt`, review the diff, and rerun public tests.
4. Deliver one `02_word_frequency_*.txt` variant. For matched specification
   comparisons, restart each variant from the same declared snapshot. The fully
   specified variant adds an explicit ASCII-punctuation contract to resolve
   ambiguity; its hidden oracle must not grade the minimally specified variants.
5. On the resulting implementation, deliver `03_generate_tests.txt` and run
   pytest. Generated tests are submissions, not the benchmark's correctness oracle.
6. Deliver `04_underspecified_optimization.txt`, review assumptions and changes,
   then invoke `05_undo.txt` through OpenCode's native command interface. Compare
   file contents and repository state before the edit and after undo. Do not
   substitute a harness reset for native undo.
7. Deliver `06_compare_models.txt` from an identical declared snapshot for each
   model; retain the exact prompt. No model or provider is selected here.

`/init` and `/undo` files contain command requests, not ordinary inference prompts.
Compatibility with the pinned OpenCode release must be checked before execution.
The workflow mirrors the TP; independent scoring and state resets are benchmark
extensions. No unattended runner, provider configuration, mutant suite or scored
run is implemented in this stage.

## Test commands

Use Python 3.10 or later and pytest 8.4.2 in a dedicated environment. From the
repository root, the public baseline command is:

```sh
python -m pytest -c benchmark/toy/pytest.ini benchmark/toy/fixture/test_toolbox.py
```

`pytest.ini` defaults to collecting the public fixture only. Always pass the
public path explicitly; never run recursive collection over an agent/evaluator
mixture. The public baseline should contain palindrome tests only, with the
space-handling case failing and the other source cases passing.

## Evaluator-only oracle

After the OpenCode process is stopped, copy the submitted `toolbox.py` into a
separate evaluator sandbox. Mount oracle tests there, never in the agent sandbox.
The explicit environment variable selects the submission; there is no fallback
to the initial fixture or the import path. In the evaluator, run a task-specific
file, for example:

```sh
TOY_SUBMISSION_ROOT=/absolute/path/to/evaluator/submission \
  python -m pytest benchmark/toy/oracle/test_palindrome.py
```

Use `test_word_frequency.py` only for the fully specified implementation variant,
and `test_temperature.py` for temperature conversion. The unresolved fixture is
expected to fail these implementation checks. Do not expose oracle output to
OpenCode or run the submitted code with maintainer credentials. Public version
control visibility of an oracle does not permit runtime access to it.
