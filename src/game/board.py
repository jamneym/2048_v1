"""Board state and movement rules for 2048."""

from __future__ import annotations

from collections.abc import Iterable

from game.config import BOARD_SIZE
from game.models import Direction

# %% Types
Cell = int | None
Row = list[Cell]
Cells = list[Row]
Position = tuple[int, int]


# %% Board state and movement
class Board:
    """A square 2048 board that owns all tile movement and merging."""

    def __init__(
        self,
        size: int = BOARD_SIZE,
        cells: Iterable[Iterable[Cell]] | None = None,
    ) -> None:
        """Create an empty board or validate a supplied starting layout."""
        # Validate the board shape before storing any state.
        if size < 2:
            raise ValueError("Board size must be at least 2.")
        self.size: int = size
        # Copy caller-provided cells so later board mutations stay internal.
        self._cells: Cells = (
            self._validate_cells(cells) if cells is not None else self._empty()
        )

    def move(self, direction: Direction) -> int:
        """Move tiles and return the score gained; return zero if unchanged."""
        # Stage 1: Reorient the board so every direction can use left-merge logic.
        transformed = self._transform_for(direction)
        moved_rows: Cells = []
        score_gained: int = 0

        # Stage 2: Compact and merge each reoriented row independently.
        for row in transformed:
            merged, gained = self._merge_line_left(row)
            moved_rows.append(merged)
            score_gained += gained

        # Stage 3: Restore the original orientation and commit only real moves.
        cells = self._restore_from(direction, moved_rows)
        if cells == self._cells:
            return 0
        self._cells = cells
        return score_gained

    def available_moves(self) -> list[Direction]:
        """Return directions that would alter the board."""
        available: list[Direction] = []
        for direction in Direction:
            # Test a copy so checking availability never changes this board.
            simulated = self.copy()
            simulated.move(direction)
            if simulated.to_list() != self.to_list():
                available.append(direction)
        return available

    def copy(self) -> Board:
        """Return an independent board with the same cells."""
        return Board(self.size, self._cells)

    def empty_cells(self) -> list[Position]:
        """Return row and column coordinates of empty cells."""
        return [
            (row_index, column_index)
            for row_index, row in enumerate(self._cells)
            for column_index, cell in enumerate(row)
            if cell is None
        ]

    def place(self, row: int, column: int, value: int) -> None:
        """Place a valid tile in an empty cell."""
        # Stage 1: Reject values and coordinates the board cannot represent.
        if value <= 0 or value & (value - 1):
            raise ValueError("Tile values must be positive powers of two.")
        if not 0 <= row < self.size or not 0 <= column < self.size:
            raise ValueError("Cell position is outside the board.")

        # Stage 2: Keep existing tiles intact, then fill the requested space.
        if self._cells[row][column] is not None:
            raise ValueError("Cannot place a tile in an occupied cell.")
        self._cells[row][column] = value

    def contains(self, value: int) -> bool:
        """Return whether the board contains at least the supplied value."""
        return any(
            cell is not None and cell >= value for row in self._cells for cell in row
        )

    def total(self) -> int:
        """Return the sum of all tile values."""
        return sum(cell for row in self._cells for cell in row if cell is not None)

    def to_list(self) -> Cells:
        """Return a defensive copy of the board cells."""
        return [row.copy() for row in self._cells]

    # %% Board helpers
    def _empty(self) -> Cells:
        """Build a square grid filled with empty cells."""
        return [[None for _ in range(self.size)] for _ in range(self.size)]

    def _validate_cells(self, cells: Iterable[Iterable[Cell]]) -> Cells:
        """Copy and validate a supplied square grid of tile values."""
        # Materialize iterable input once so its dimensions and values can be checked.
        validated = [list(row) for row in cells]
        if len(validated) != self.size or any(
            len(row) != self.size for row in validated
        ):
            raise ValueError("Board cells must match the configured board size.")
        for row in validated:
            for cell in row:
                if cell is not None and (cell <= 0 or cell & (cell - 1)):
                    raise ValueError("Tile values must be positive powers of two.")
        return validated

    def _transform_for(self, direction: Direction) -> Cells:
        """Reorient cells so a requested move reads as moving left."""
        cells = self.to_list()
        if direction is Direction.LEFT:
            return cells
        if direction is Direction.RIGHT:
            return [list(reversed(row)) for row in cells]
        transposed = self._transpose(cells)
        if direction is Direction.UP:
            return transposed
        return [list(reversed(row)) for row in transposed]

    def _restore_from(
        self, direction: Direction, cells: Cells
    ) -> Cells:
        """Undo the orientation change used for a left-oriented move."""
        if direction is Direction.LEFT:
            return cells
        if direction is Direction.RIGHT:
            return [list(reversed(row)) for row in cells]
        if direction is Direction.UP:
            return self._transpose(cells)
        return self._transpose([list(reversed(row)) for row in cells])

    def _merge_line_left(self, row: Row) -> tuple[Row, int]:
        """Compact one row left, merging each equal adjacent pair once."""
        # Stage 1: Remove gaps because empty cells cannot participate in a merge.
        tiles = [cell for cell in row if cell is not None]
        merged: Row = []
        score_gained: int = 0
        index: int = 0

        # Stage 2: Walk left to right, consuming a matching neighbour when present.
        while index < len(tiles):
            tile = tiles[index]
            if index + 1 < len(tiles) and tile == tiles[index + 1]:
                assert tile is not None
                tile *= 2
                score_gained += tile
                # Skip the consumed neighbour so a tile merges at most once per move.
                index += 1
            merged.append(tile)
            index += 1
        # Stage 3: Restore the row length by placing remaining empty cells on the right.
        return merged + [None] * (self.size - len(merged)), score_gained

    @staticmethod
    def _transpose(cells: Cells) -> Cells:
        """Swap rows and columns in a square cell grid."""
        return [list(row) for row in zip(*cells, strict=True)]
