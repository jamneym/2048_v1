import random

import pytest

from game.board import Board
from game.tile_generator import TileGenerator


def test_place_adds_one_tile_to_an_empty_cell() -> None:
    board = Board(cells=[[None] * 4 for _ in range(4)])
    generator = TileGenerator(random.Random(1), probability_of_four=0)

    placed = generator.place(board)

    assert placed is True
    assert sum(cell is not None for row in board.to_list() for cell in row) == 1


def test_place_returns_false_when_board_is_full() -> None:
    board = Board(cells=[[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]])
    generator = TileGenerator(random.Random(1), probability_of_four=0)

    assert generator.place(board) is False


@pytest.mark.parametrize(("probability", "expected_value"), [(0, 2), (1, 4)])
def test_place_generates_only_configured_tile_values(
    probability: float, expected_value: int
) -> None:
    board = Board()
    generator = TileGenerator(random.Random(1), probability)

    assert generator.place(board) is True

    values = [cell for row in board.to_list() for cell in row if cell is not None]
    assert values == [expected_value]


def test_initial_count_uses_the_configured_range() -> None:
    generator = TileGenerator(random.Random(1), probability_of_four=0)

    assert 2 <= generator.initial_count(2, 4) <= 4
