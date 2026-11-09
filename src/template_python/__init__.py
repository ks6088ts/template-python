"""Reusable building blocks for the template project."""

from importlib.metadata import PackageNotFoundError, version

from template_python.core import greeting

try:
    __version__ = version("template-python")
except PackageNotFoundError:  # pragma: no cover - only for an uninstalled source tree
    __version__ = "0.0.0+unknown"

__all__ = ["__version__", "greeting"]
