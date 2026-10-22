"""Pick which implementation the tests run against.

By default the tests import *your* code: ``lab/<lab_name>/exercise.py``.

Teachers can check the reference solutions with::

    LAB_SOLUTION=1 uv run pytest lab

which imports ``lab_solutions/<lab_name>.py`` (or the package of the same
name) instead.
"""

import importlib
import os
from types import ModuleType


def load(lab: str, submodule: str | None = None) -> ModuleType:
    if os.getenv("LAB_SOLUTION"):
        name = f"lab_solutions.{lab}"
    else:
        name = f"lab.{lab}.exercise"
    if submodule:
        name = f"{name}.{submodule}"
    return importlib.import_module(name)
