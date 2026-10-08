# Level 1 prompts

The seven `.txt` task files contain the exact French inference prompts. Send their
contents verbatim. They contain no model or provider names. Do not append metadata,
oracle details or a deployment-specific preamble.

[`metadata.json`](metadata.json) records prompt-set version `1.0.0`, file hashes,
source digests, TP section/page references, wording provenance and extensions.
Hashes cover exact UTF-8 bytes, including final newlines. Commit wording and
metadata together; update the version and hashes whenever wording changes.

| Prompt | Methodological origin | Wording and benchmark additions |
| --- | --- | --- |
| `01_bugfix.txt` | TP §3.2, p. 4, task 1 | TP example with normalized punctuation |
| `02_word_frequency_minimal.txt` | TP §3.2, p. 4, task 2 | TP minimal example with a final full stop |
| `03_word_frequency_intermediate.txt` | TP §3.2, p. 4, task 2 | TP dictionary example with normalized spacing/punctuation |
| `04_word_frequency_explicit.txt` | TP §3.2, p. 4, task 2, plus benchmark extensions | Adds precise separators, accent/digit handling and empty-input behavior |
| `05_generate_tests.txt` | TP §3.2, p. 5, task 3, plus benchmark extensions | New wording; separate output file and protection of implementation/existing tests |
| `06_underspecified_optimization.txt` | TP §3.2, p. 5, task 4 | TP example with normalized capitalization/punctuation |
| `07_celsius.txt` | TP §3.2, p. 5, task 5 | New provider-independent wording for the TP's named conversion task |

Methodological origin does not imply a verbatim quotation: the metadata records
that distinction. The three specification variants are alternatives. For
independent comparisons, reset to the same declared snapshot before each variant.
The word-frequency oracle grades only the explicit variant; it must not penalize
the minimal/intermediate prompts for absent requirements. Test generation uses
the chosen implementation and its previously supplied specification.

`00_init.txt` and `05_undo.txt` remain native workflow command requests, outside
the seven inference prompts. Use the metadata's explicit prompt order instead of
sorting or sending every `.txt` file. Native undo follows the optimization step.
Deliver all prompts through the evaluated runtime only; infrastructure authors
must not execute or solve these tasks. No fixture or oracle is changed here.
