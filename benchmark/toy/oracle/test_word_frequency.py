"""Checks for the fully specified variant only, not the minimal prompts."""

import pytest


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", {}),
        (" \t\n.,!?-_'", {}),
        ("Bonjour bonjour BONJOUR", {"bonjour": 3}),
        ("chat,chien;chat!", {"chat": 2, "chien": 1}),
        ("un\tdeux\nun", {"un": 2, "deux": 1}),
        ("L'été arc-en-ciel", {"l": 1, "été": 1, "arc": 1, "en": 1, "ciel": 1}),
        ("ÉTÉ été ete", {"été": 2, "ete": 1}),
        ("version 2 VERSION 2 10", {"version": 2, "2": 2, "10": 1}),
        ('[oui] (non): "oui"', {"oui": 2, "non": 1}),
    ],
)
def test_word_frequency_full_contract(submitted_toolbox, text, expected):
    result = submitted_toolbox.word_frequency(text)
    assert isinstance(result, dict)
    assert result == expected
