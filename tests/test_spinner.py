from __future__ import annotations

import time

import pytest

import griphtui as gui


def test_spinner_runs_and_stops() -> None:
    with gui.spinner("working") as s:
        time.sleep(0.1)
        assert s.is_running
        s.update("still working")
        time.sleep(0.1)
    assert not s.is_running


def test_spinner_update_is_thread_safe() -> None:
    s = gui.spinner("initial")
    with s:
        for i in range(50):
            s.update(f"tick {i}")
        time.sleep(0.05)
    assert not s.is_running


def test_spinner_exception_propagates() -> None:
    with pytest.raises(RuntimeError):
        with gui.spinner("failing"):
            raise RuntimeError("boom")
