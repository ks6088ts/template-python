"""Shared fixtures for the test suite."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from template_python import settings as settings_module

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(autouse=True)
def _isolate_settings_cache() -> Iterator[None]:
    """Ensure each test sees a freshly-built :class:`Settings` instance.

    ``get_project_settings`` is memoised with ``lru_cache`` for production
    use. During tests we want every test to observe the current process
    environment, so we clear the cache before and after each test.
    """
    settings_module.get_project_settings.cache_clear()
    try:
        yield
    finally:
        settings_module.get_project_settings.cache_clear()


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """Remove project-related environment variables for the duration of the test."""
    for key in ("PROJECT_NAME", "PROJECT_LOG_LEVEL"):
        monkeypatch.delenv(key, raising=False)
    return monkeypatch
