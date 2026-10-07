"""Independent expected values; no task implementation or reference solution."""

import pytest


@pytest.mark.parametrize(
    ("celsius", "expected"),
    [(0, 32), (100, 212), (-40, -40), (37, 98.6), (12.5, 54.5), (-273.15, -459.67)],
)
def test_celsius_to_fahrenheit_contract(submitted_toolbox, celsius, expected):
    result = submitted_toolbox.celsius_to_fahrenheit(celsius)
    assert result == pytest.approx(expected, rel=1e-9, abs=1e-9)
