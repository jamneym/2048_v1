# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: title,-all
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
# ---

# %%
"""CLI entry point for the 2048 game."""

from game.game import Game


# %% CLI entry point
def main() -> None:
    """Launch the CLI game."""
    # Create the application state, then hand control to its input/rendering loop.
    game: Game = Game()
    game.run()

if __name__ == "__main__":
    main()
