from game.ai import MoveAdvisor
from game.board import Board
from game.models import Direction


def test_suggestion_is_legal_and_does_not_mutate_the_board() -> None:
    board = Board(
        cells=[[2, 4, None, None], [8, 8, None, None], [None] * 4, [None] * 4]
    )
    before = board.to_list()

    suggestion = MoveAdvisor().suggest(board)

    assert suggestion in board.available_moves()
    assert board.to_list() == before


def test_suggestion_returns_none_when_no_moves_remain() -> None:
    board = Board(cells=[[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]])

    assert MoveAdvisor().suggest(board) is None


def test_suggestion_returns_one_of_the_legal_directions() -> None:
    board = Board(
        cells=[
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [2, 4, 2, 4],
        ]
    )

    legal_moves = board.available_moves()

    assert legal_moves == [Direction.UP, Direction.DOWN]
    assert MoveAdvisor().suggest(board) in legal_moves
