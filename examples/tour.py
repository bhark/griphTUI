"""Interactive tour of every griphtui primitive."""

from __future__ import annotations

import time

import griphtui as gui


def main() -> None:
    gui.intro("GriphTUI")

    gui.section("Scratching the surface")
    name = gui.text("Who are you?", default="Anonymous")
    token = gui.password("Tell me a secret")
    proceed = gui.confirm("Wanna dive deeper?", default=True)
    if not proceed:
        gui.outro("Bye!")
        return

    direction = gui.select(
        "You come to a cross in the road. Where to?",
        [("My way", "my-way"), ("The highway", "the-highway"), ("The Queens way", "the-queens-way")],
    )
    meanings = gui.multiselect(
        "What is the meaning of life?",
        [
            ("Returning to the archaic", "archaic", True),
            ("Forty-two", "forty-two", False),
            ("Steam locomotives", "steam-locomotives", False),
        ],
    )

    gui.section("All is movement")
    with gui.spinner("Warming up...") as s:
        time.sleep(0.8)
        s.update("Deliberating...")
        time.sleep(0.8)
        s.update("Pondering...")
        time.sleep(0.6)

    gui.section("That's a wrap")
    gui.info(f"Hello {name}, with the well-kept {len(token)} chars secret)")
    gui.step(f"You chose {direction}, and your life has {len(meanings)} meaning(s)")
    gui.success("Looking good!")
    gui.warn("Kind of shaky...")
    gui.error("It's all gone wrong.")

    gui.outro("That's all, folks")


if __name__ == "__main__":
    main()
