from __future__ import annotations

import io

from rich.console import Console

import griphtui as gui


def make_console() -> tuple[Console, io.StringIO]:
    buf = io.StringIO()
    return Console(file=buf, force_terminal=False, width=80, highlight=False), buf


def test_intro_escapes_markup() -> None:
    console, buf = make_console()
    gui.intro("release [v1.0]", console=console)
    assert "release [v1.0]" in buf.getvalue()


def test_outro_escapes_markup() -> None:
    console, buf = make_console()
    gui.outro("done [WIP]", console=console)
    assert "done [WIP]" in buf.getvalue()


def test_section_escapes_markup() -> None:
    console, buf = make_console()
    gui.section("step [2/5]", console=console)
    assert "step [2/5]" in buf.getvalue()
