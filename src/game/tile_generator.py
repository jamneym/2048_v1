"""Random tile generation for 2048."""

from __future__ import annotations

import random

from game.board import Board


# %% Tile generation
class TileGenerator:
    """Choose how many tiles to add and where new tiles appear."""

    def __init__(self, rng: random.Random, probability_of_four: float) -> None:
        """Create a generator with injected randomness and tile-value odds."""
        if not 0 <= probability_of_four <= 1:
            raise ValueError("Probability of four must be between 0 and 1.")
        self._rng: random.Random = rng
        self._probability_of_four: float = probability_of_four

    def place(self, board: Board, value: int | None = None) -> bool:
        """Place one tile in a random empty cell, if one exists."""
        # Stage 1: Identify whether placement is possible before choosing a location.
        empty_cells = board.empty_cells()
        if not empty_cells:
            return False

        # Stage 2: Choose a location, then use an explicit or randomly generated value.
        row, column = self._rng.choice(empty_cells)
        board.place(row, column, value if value is not None else self._value())
        return True

    def initial_count(self, minimum: int, maximum: int) -> int:
        """Return a random initial tile count from the configured range."""
        return self._rng.randint(minimum, maximum)

    # %% Tile value selection
    def _value(self) -> int:
        """Return 4 at the configured probability; otherwise return 2."""
        return 4 if self._rng.random() < self._probability_of_four else 2
