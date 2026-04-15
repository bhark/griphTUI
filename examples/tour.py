"""Interactive tour of every griphtui primitive."""

from __future__ import annotations

import sys
import time
from typing import TypeVar

import griphtui as gtui

R = TypeVar("R")


def _bail(value: R | gtui.Cancel) -> R:
    if gtui.is_cancel(value):
        gtui.outro("Cancelled by user")
        sys.exit(0)
    return value


def main() -> None:
    gtui.intro("GriphTUI")

    gtui.section("Scratching the surface")
    name = _bail(
        gtui.text(
            "Who are you?",
            default="Anonymous",
            validate=lambda s: "at least 2 chars" if len(s) < 2 else None,
        )
    )
    token = _bail(
        gtui.password(
            "Tell me a secret",
            validate=lambda s: "at least 4 chars" if len(s) < 4 else None,
        )
    )
    proceed = _bail(gtui.confirm("Wanna dive deeper?", default=True))
    if not proceed:
        gtui.outro("Bye!")
        return

    direction = _bail(
        gtui.select(
            "You come to a cross in the road. Where to?",
            [("My way", "my-way"), ("The highway", "the-highway"), ("The Queens way", "the-queens-way")],
        )
    )
    meanings = _bail(
        gtui.multiselect(
            "What is the meaning of life?",
            [
                ("Returning to the archaic", "archaic", True),
                ("Forty-two", "forty-two", False),
                ("Steam locomotives", "steam-locomotives", False),
            ],
        )
    )

    gtui.note(
        [
            f"name:     {name}",
            f"secret:   {'*' * len(token)}",
            f"path:     {direction}",
            f"meanings: {', '.join(meanings) or 'none'}",
        ],
        title="Your answers",
    )
    if not _bail(gtui.confirm("Does that look right?", default=True)):
        gtui.outro("No worries, maybe next time")
        return

    gtui.section("All is movement")
    with gtui.spinner("Warming up...") as s:
        time.sleep(0.8)
        s.update("Deliberating...")
        time.sleep(0.8)
        s.update("Pondering...")
        time.sleep(0.6)

    gtui.section("That's a wrap")
    gtui.info(f"Hello {name}, with the well-kept {len(token)} chars secret")
    gtui.step(f"You chose {direction}, and your life has {len(meanings)} meaning(s)")
    gtui.success("Looking good!")
    gtui.warn("Kind of shaky...")
    gtui.error("It's all gone wrong.")

    gtui.outro("That's all, folks")


if __name__ == "__main__":
    main()
