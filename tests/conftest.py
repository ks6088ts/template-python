import logging
import os
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    """Keep tests independent of the developer's shell, ``.env`` file, and logging state."""
    for key in os.environ:
        if key.upper().startswith("PROJECT_"):
            monkeypatch.delenv(key)
    monkeypatch.chdir(tmp_path)

    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    yield
    root.handlers[:] = handlers
    root.setLevel(level)
