from __future__ import annotations

import sys
import threading
from types import TracebackType

from ._glyphs import BAR, SPINNER_FRAMES
from .status import error as _error_line, success as _success_line

_INTERVAL = 0.08
_CLEAR = "\r\033[K"


class Spinner:
    def __init__(self, label: str) -> None:
        self._label = label
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._done_message: str | None = None
        self._fail_message: str | None = None

    def update(self, label: str) -> None:
        with self._lock:
            self._label = label

    def done(self, message: str) -> None:
        with self._lock:
            self._done_message = message

    def fail(self, message: str) -> None:
        with self._lock:
            self._fail_message = message

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _run(self) -> None:
        out = sys.stdout
        i = 0
        while not self._stop.is_set():
            with self._lock:
                label = self._label
            frame = SPINNER_FRAMES[i % len(SPINNER_FRAMES)]
            out.write(f"{_CLEAR} {BAR}  {frame} {label}")
            out.flush()
            i += 1
            self._stop.wait(_INTERVAL)
        out.write(_CLEAR)
        out.flush()

    def __enter__(self) -> "Spinner":
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join()
        with self._lock:
            done, fail = self._done_message, self._fail_message
        if exc_type is not None and fail is not None:
            _error_line(fail)
        elif exc_type is None and done is not None:
            _success_line(done)


def spinner(label: str) -> Spinner:
    return Spinner(label)
