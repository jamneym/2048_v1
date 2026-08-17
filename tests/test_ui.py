from io import StringIO

import pytest

from game import UI


def test_render_formats_a_four_by_four_board() -> None:
    board = [
        [2, 4, None, None],
        [None, 8, None, None],
        [None, None, 16, None],
        [None, None, None, 32],
    ]

    rendered = UI().render(board)

    assert rendered == (
        "+------+------+------+------+\n"
        "|  2   |  4   |      |      |\n"
        "+------+------+------+------+\n"
        "|      |  8   |      |      |\n"
        "+------+------+------+------+\n"
        "|      |      |  16  |      |\n"
        "+------+------+------+------+\n"
        "|      |      |      |  32  |\n"
        "+------+------+------+------+"
    )


def test_refresh_clears_and_writes_the_board() -> None:
    output = StringIO()

    UI(output).refresh([[0, 0, 0, 0]] * 4)

    assert output.getvalue().startswith("\033[2J\033[H+------+------+------+------+\n")


def test_render_rejects_non_four_by_four_boards() -> None:
    with pytest.raises(ValueError, match="four rows of four cells"):
        UI().render([[2]])
