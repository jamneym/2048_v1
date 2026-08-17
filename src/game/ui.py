"""CLI presentation for a 2048 board."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import TextIO

from game.config import APP_NAME, BOARD_SIZE, WINNING_TILE
from game.models import GameStatus

# %% Types
Cell = int | None
Board = Sequence[Sequence[Cell]]


# %% Terminal user interface
class UI:
    """Render a supplied 4 by 4 board without owning game state."""

    def __init__(self, output: TextIO | None = None) -> None:
        """Create a UI that writes to standard output by default."""
        self._output: TextIO = output if output is not None else sys.stdout

    def render(self, board: Board) -> str:
        """Return a formatted representation of a 4 by 4 board."""
        # Stage 1: Reject malformed input and size cells for the largest tile.
        self._validate_board(board)
        cell_width = max(
            [4, *(len(str(cell)) for row in board for cell in row if cell)]
        )
        border = "+" + "+".join("-" * (cell_width + 2) for _ in range(BOARD_SIZE)) + "+"
        rows = [border]

        # Stage 2: Format each board row between matching horizontal borders.
        for row in board:
            values = ("" if cell is None or cell == 0 else str(cell) for cell in row)
            rows.append(
                "|" + "|".join(f" {value:^{cell_width}} " for value in values) + "|"
            )
            rows.append(border)

        return "\n".join(rows)

    def refresh(
        self,
        board: Board,
        score: int | None = None,
        status: GameStatus | None = None,
        hint: str | None = None,
    ) -> None:
        """Clear the terminal and display the latest board."""
        # Stage 1: Assemble optional game information above the board.
        heading = ""
        if score is not None:
            heading = f"{APP_NAME}   Score: {score}\n"
        if status is GameStatus.WON:
            heading += f"You reached {WINNING_TILE}. You win!\n"
        elif status is GameStatus.LOST:
            heading += "No moves remain. Game over.\n"
        if hint is not None:
            heading += f"{hint}\n"

        # Stage 2: Clear the previous screen, then print the completed frame.
        # ANSI escapes clear the terminal and move the cursor to its top-left corner.
        print("\033[2J\033[H" + heading + self.render(board), file=self._output)

    def message(self, text: str) -> None:
        """Display a short message below the rendered board."""
        print(text, file=self._output)

    def refresh_about(self, about_message: str) -> None:
        """Clear the terminal and display the full-screen About page."""
        # Render the About page separately so it can replace the normal game frame.
        print(
            "\033[2J\033[H"
            f"{APP_NAME} - About\n\n"
            f"{about_message.strip()}\n\n"
            "Press X to return to the game.",
            file=self._output,
        )

    @staticmethod
    def _validate_board(board: Board) -> None:
        """Ensure the UI receives the fixed 4 by 4 game layout."""
        if len(board) != BOARD_SIZE or any(len(row) != BOARD_SIZE for row in board):
            message = "A 2048 board must contain exactly four rows of four cells."
            raise ValueError(message)
