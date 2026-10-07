"""Benchmark-authored checks; not public tests from the TP archive."""

import pytest


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", True),
        ("   ", True),
        ("x", True),
        ("RaDaR", True),
        ("  Ka yak ", True),
        ("É t é", True),
        ("a  b a", True),
        ("Python", False),
        ("ab ca", False),
        ("a!a", True),
        ("a!ba", False),
    ],
)
def test_palindrome_contract(submitted_toolbox, text, expected):
    result = submitted_toolbox.is_palindrome(text)
    assert isinstance(result, bool)
    assert result is expected
