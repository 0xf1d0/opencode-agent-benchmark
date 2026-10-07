"""Load only an explicitly selected submission, outside the agent workspace."""

import importlib.util
import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def submitted_toolbox():
    submission_root = os.environ.get("TOY_SUBMISSION_ROOT")
    if not submission_root:
        raise pytest.UsageError(
            "Set TOY_SUBMISSION_ROOT to the evaluator-only submission directory."
        )

    module_path = Path(submission_root).resolve() / "toolbox.py"
    if not module_path.is_file():
        raise pytest.UsageError(f"Submission is missing toolbox.py: {module_path}")

    spec = importlib.util.spec_from_file_location("submitted_toolbox", module_path)
    if spec is None or spec.loader is None:
        raise pytest.UsageError(f"Cannot load submission: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
