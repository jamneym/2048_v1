import pytest

from game.board import Board
from game.models import Direction

REQUIREMENTS_BOARD = [
    [None, 8, 2, 2],
    [4, 2, None, 2],
    [None, None, None, None],
    [None, None, None, 2],
]


@pytest.mark.parametrize(
    ("direction", "expected"),
    [
        (
            Direction.LEFT,
            [
                [8, 4, None, None],
                [4, 4, None, None],
                [None, None, None, None],
                [2, None, None, None],
            ],
        ),
        (
            Direction.RIGHT,
            [
                [None, None, 8, 4],
                [None, None, 4, 4],
                [None, None, None, None],
                [None, None, None, 2],
            ],
        ),
        (
            Direction.UP,
            [
                [4, 8, 2, 4],
                [None, 2, None, 2],
                [None, None, None, None],
                [None, None, None, None],
            ],
        ),
        (
            Direction.DOWN,
            [
                [None, None, None, None],
                [None, None, None, None],
                [None, 8, None, 2],
                [4, 2, 2, 4],
            ],
        ),
    ],
)
def test_moves_match_the_requirement_examples(
    direction: Direction, expected: list[list[int | None]]
) -> None:
    board = Board(cells=REQUIREMENTS_BOARD)

    board.move(direction)

    assert board.to_list() == expected


def test_left_move_merges_each_pair_once() -> None:
    board = Board(cells=[[2, 2, 2, 2], [None] * 4, [None] * 4, [None] * 4])

    score = board.move(Direction.LEFT)

    assert score == 8
    assert board.to_list()[0] == [4, 4, None, None]


def test_moves_transform_the_board_for_each_direction() -> None:
    board = Board(
        cells=[[2, None, None, None], [2, None, None, None], [None] * 4, [None] * 4]
    )

    board.move(Direction.DOWN)

    assert board.to_list()[-1][0] == 4
    assert board.available_moves() == [Direction.RIGHT, Direction.UP]
