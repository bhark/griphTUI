"""griphtui - clack-style terminal UI primitives."""

from __future__ import annotations

from .layout import intro, outro, section
from .prompts import Option, confirm, multiselect, password, select, text
from .spinner import Spinner, spinner
from .status import error, info, step, success, warn

__all__ = [
    "Option",
    "Spinner",
    "confirm",
    "error",
    "info",
    "intro",
    "multiselect",
    "outro",
    "password",
    "section",
    "select",
    "spinner",
    "step",
    "success",
    "text",
    "warn",
]

from ._version import __version__  # noqa: E402
