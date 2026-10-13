import pytest

from template_python.core import greeting


def test_greeting_normalizes_name() -> None:
    assert greeting("  Ada  ") == "Hello, Ada!"


def test_greeting_rejects_blank_name() -> None:
    with pytest.raises(ValueError, match="name must not be blank"):
        greeting("  ")
