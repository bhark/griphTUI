"""Interactive tour of every griphtui primitive."""

from __future__ import annotations

import time

import griphtui as gtui


def main() -> None:
    gtui.intro("GriphTUI")

    gtui.section("Scratching the surface")
    name = gtui.text("Who are you?", default="Anonymous")
    token = gtui.password("Tell me a secret")
    proceed = gtui.confirm("Wanna dive deeper?", default=True)
    if not proceed:
        gtui.outro("Bye!")
        return

    direction = gtui.select(
        "You come to a cross in the road. Where to?",
        [("My way", "my-way"), ("The highway", "the-highway"), ("The Queens way", "the-queens-way")],
    )
    meanings = gtui.multiselect(
        "What is the meaning of life?",
        [
            ("Returning to the archaic", "archaic", True),
            ("Forty-two", "forty-two", False),
            ("Steam locomotives", "steam-locomotives", False),
        ],
    )

    gtui.section("All is movement")
    with gtui.spinner("Warming up...") as s:
        time.sleep(0.8)
        s.update("Deliberating...")
        time.sleep(0.8)
        s.update("Pondering...")
        time.sleep(0.6)

    gtui.section("That's a wrap")
    gtui.info(f"Hello {name}, with the well-kept {len(token)} chars secret)")
    gtui.step(f"You chose {direction}, and your life has {len(meanings)} meaning(s)")
    gtui.success("Looking good!")
    gtui.warn("Kind of shaky...")
    gtui.error("It's all gone wrong.")

    gtui.outro("That's all, folks")


if __name__ == "__main__":
    main()
