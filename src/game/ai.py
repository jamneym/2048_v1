"""Offline expectimax move advisor for the 2048 CLI."""

from __future__ import annotations

from game.board import Board
from game.config import (
    AI_CORNER_WEIGHT,
    AI_EMPTY_CELL_WEIGHT,
    AI_LOST_BOARD_PENALTY,
    AI_MERGE_OPPORTUNITY_WEIGHT,
    AI_MONOTONICITY_WEIGHT,
    AI_ROUGHNESS_WEIGHT,
    AI_SEARCH_DEPTH,
    AI_WINNING_BOARD_BONUS,
    PROBABILITY_OF_FOUR,
    WINNING_TILE,
)
from game.models import Direction

# %% Types
type BoardKey = tuple[tuple[int | None, ...], ...]
type CacheKey = tuple[str, int, BoardKey]


# %% Move advisor
class MoveAdvisor:
    """Recommend a move with bounded offline expectimax search.

    Player nodes select the highest-value legal move. Chance nodes average all
    possible tile spawns using the game's configured 2/4 probability. Leaf
    boards are ranked with hand-tuned survival heuristics; no model, network,
    credentials, or mutation of the supplied board is required.
    """

    def __init__(self) -> None:
        """Create a cache shared by the simulated states of one suggestion."""
        self._cache: dict[CacheKey, float] = {}

    def suggest(self, board: Board) -> Direction | None:
        """Return the best valid direction without changing the supplied board."""
        # A cache only applies to one immutable input position.
        self._cache.clear()
        best_direction: Direction | None = None
        best_score = float("-inf")

        # Simulate each move, then evaluate its random tile spawn.
        for direction in board.available_moves():
            simulated = self._moved(board, direction)
            score = self._chance_value(simulated, AI_SEARCH_DEPTH)
            if score > best_score:
                best_direction = direction
                best_score = score
        return best_direction

    # %% Expectimax search
    def _player_value(self, board: Board, depth: int) -> float:
        """Return the value of the best move available to the player."""
        key = ("player", depth, self._board_key(board))
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        legal_moves = board.available_moves()
        if depth <= 0 or not legal_moves:
            value = float(self._evaluate(board))
        else:
            value = max(
                self._chance_value(self._moved(board, direction), depth)
                for direction in legal_moves
            )
        self._cache[key] = value
        return value

    def _chance_value(self, board: Board, depth: int) -> float:
        """Average player values across every possible random tile spawn."""
        key = ("chance", depth, self._board_key(board))
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        if depth <= 0:
            value = float(self._evaluate(board))
        else:
            empty_cells = board.empty_cells()
            if not empty_cells:
                value = self._player_value(board, depth - 1)
            else:
                # Average every equally likely empty location and its 2/4 spawn odds.
                value = sum(
                    (1 - PROBABILITY_OF_FOUR)
                    * self._player_value(
                        self._spawned(board, row, column, 2), depth - 1
                    )
                    + PROBABILITY_OF_FOUR
                    * self._player_value(
                        self._spawned(board, row, column, 4), depth - 1
                    )
                    for row, column in empty_cells
                ) / len(empty_cells)
        self._cache[key] = value
        return value

    # %% Board evaluation
    def _evaluate(self, board: Board) -> int:
        """Score a leaf board by its likelihood of remaining playable."""
        if board.contains(WINNING_TILE):
            return AI_WINNING_BOARD_BONUS
        if not board.available_moves():
            return -AI_LOST_BOARD_PENALTY

        cells = board.to_list()
        return ( 0
            + AI_EMPTY_CELL_WEIGHT * len(board.empty_cells())
            + AI_MERGE_OPPORTUNITY_WEIGHT * self._merge_opportunities(cells)
            + AI_MONOTONICITY_WEIGHT * self._monotonicity(cells)
            - AI_ROUGHNESS_WEIGHT * self._roughness(cells)
            + AI_CORNER_WEIGHT * self._largest_tile_is_in_a_corner(cells)
        )

    @staticmethod
    def _moved(board: Board, direction: Direction) -> Board:
        """Return an independent board after one legal simulated move."""
        simulated = board.copy()
        simulated.move(direction)
        return simulated

    @staticmethod
    def _spawned(board: Board, row: int, column: int, value: int) -> Board:
        """Return an independent board with one hypothetical spawned tile."""
        simulated = board.copy()
        simulated.place(row, column, value)
        return simulated

    @staticmethod
    def _board_key(board: Board) -> BoardKey:
        """Create a hashable representation suitable for the per-hint cache."""
        return tuple(tuple(row) for row in board.to_list())

    @staticmethod
    def _merge_opportunities(cells: list[list[int | None]]) -> int:
        """Count adjacent equal tiles that can become a future merge."""
        opportunities = 0
        for row_index, row in enumerate(cells):
            for column_index, value in enumerate(row):
                if value is None:
                    continue
                if column_index + 1 < len(row) and value == row[column_index + 1]:
                    opportunities += 1
                if (
                    row_index + 1 < len(cells)
                    and value == cells[row_index + 1][column_index]
                ):
                    opportunities += 1
        return opportunities

    @staticmethod
    def _monotonicity(cells: list[list[int | None]]) -> int:
        """Reward boards whose values descend away from one of four corners."""
        values = [
            [cell.bit_length() if cell is not None else 0 for cell in row]
            for row in cells
        ]
        left = sum(
            max(values[row][column] - values[row][column + 1], 0)
            for row in range(len(values))
            for column in range(len(values[row]) - 1)
        )
        right = sum(
            max(values[row][column + 1] - values[row][column], 0)
            for row in range(len(values))
            for column in range(len(values[row]) - 1)
        )
        top = sum(
            max(values[row][column] - values[row + 1][column], 0)
            for row in range(len(values) - 1)
            for column in range(len(values[row]))
        )
        bottom = sum(
            max(values[row + 1][column] - values[row][column], 0)
            for row in range(len(values) - 1)
            for column in range(len(values[row]))
        )
        return max(left + top, left + bottom, right + top, right + bottom)

    @staticmethod
    def _roughness(cells: list[list[int | None]]) -> int:
        """Measure logarithmic differences between neighbouring non-empty tiles."""
        roughness = 0
        for row_index, row in enumerate(cells):
            for column_index, value in enumerate(row):
                if value is None:
                    continue
                right = row[column_index + 1] if column_index + 1 < len(row) else None
                if right is not None:
                    roughness += abs(value.bit_length() - right.bit_length())
                below = (
                    cells[row_index + 1][column_index]
                    if row_index + 1 < len(cells)
                    else None
                )
                if below is not None:
                    roughness += abs(value.bit_length() - below.bit_length())
        return roughness

    @staticmethod
    def _largest_tile_is_in_a_corner(cells: list[list[int | None]]) -> int:
        """Return one when a largest tile is anchored in any board corner."""
        largest_tile = max(cell or 0 for row in cells for cell in row)
        corners = (cells[0][0], cells[0][-1], cells[-1][0], cells[-1][-1])
        return int(largest_tile in corners)
