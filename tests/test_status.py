from __future__ import annotations

import io

from rich.console import Console

import griphtui as gui


def make_console() -> tuple[Console, io.StringIO]:
    buf = io.StringIO()
    return Console(file=buf, force_terminal=False, width=80, highlight=False), buf


GLYPH = "\u25cf"


def test_info_renders_prefix() -> None:
    console, buf = make_console()
    gui.info("hello", console=console)
    assert f"{GLYPH} hello" in buf.getvalue()


def test_step_renders_prefix() -> None:
    console, buf = make_console()
    gui.step("hello", console=console)
    assert f"{GLYPH} hello" in buf.getvalue()


def test_success_renders_prefix() -> None:
    console, buf = make_console()
    gui.success("hello", console=console)
    assert f"{GLYPH} hello" in buf.getvalue()


def test_warn_renders_prefix() -> None:
    console, buf = make_console()
    gui.warn("hello", console=console)
    assert f"{GLYPH} hello" in buf.getvalue()


def test_error_renders_prefix() -> None:
    console, buf = make_console()
    gui.error("hello", console=console)
    assert f"{GLYPH} hello" in buf.getvalue()


def test_message_with_brackets_is_not_interpreted_as_markup() -> None:
    console, buf = make_console()
    gui.info("pick [red] or [blue]", console=console)
    assert "pick [red] or [blue]" in buf.getvalue()


def test_status_lines_are_framed() -> None:
    for fn in (gui.info, gui.step, gui.success, gui.warn, gui.error):
        console, buf = make_console()
        fn("hi", console=console)
        assert buf.getvalue().startswith(f" \u2502  {GLYPH} hi")


def test_status_lines_self_terminate_with_trailing_bar() -> None:
    for fn in (gui.info, gui.step, gui.success, gui.warn, gui.error):
        console, buf = make_console()
        fn("hi", console=console)
        assert buf.getvalue().splitlines()[-1].rstrip() == " \u2502"
