from __future__ import annotations

import random
from io import StringIO
from types import SimpleNamespace

from pytest import MonkeyPatch

from game.board import Board
from game.config import INITIAL_TILES_MAX, INITIAL_TILES_MIN
from game.game import Game
from game.models import Direction, GameStatus
from game.ui import UI


def test_valid_move_generates_one_tile_and_updates_score() -> None:
    board = Board(cells=[[2, 2, None, None], [None] * 4, [None] * 4, [None] * 4])
    game = Game(board=board, rng=random.Random(4))

    result = game.move(Direction.LEFT)

    assert result.changed is True
    assert result.score_gained == 4
    assert game.score == board.total()
    assert sum(cell is not None for row in board.to_list() for cell in row) == 2


def test_invalid_move_does_not_generate_a_tile() -> None:
    board = Board(cells=[[2, None, None, None], [None] * 4, [None] * 4, [None] * 4])
    game = Game(board=board, rng=random.Random(4))

    result = game.move(Direction.LEFT)

    assert result.changed is False
    assert board.to_list() == [
        [2, None, None, None],
        [None] * 4,
        [None] * 4,
        [None] * 4,
    ]


def test_game_marks_a_winning_move() -> None:
    board = Board(cells=[[1024, 1024, None, None], [None] * 4, [None] * 4, [None] * 4])
    game = Game(board=board)

    result = game.move(Direction.LEFT)

    assert result.status is GameStatus.WON


def test_new_game_starts_with_the_configured_number_of_twos() -> None:
    game = Game(rng=random.Random(1))

    tiles = [cell for row in game.board.to_list() for cell in row if cell is not None]

    assert INITIAL_TILES_MIN <= len(tiles) <= INITIAL_TILES_MAX
    assert set(tiles) == {2}


def test_restart_replaces_the_board_and_resets_the_score() -> None:
    board = Board(cells=[[2, 2, None, None], [None] * 4, [None] * 4, [None] * 4])
    game = Game(board=board, rng=random.Random(4))
    game.move(Direction.LEFT)

    game.restart()

    assert game.score == game.board.total()
    assert game.status is GameStatus.IN_PROGRESS
    assert game.board is not board
    assert 12 <= len(game.board.empty_cells()) <= 14


def test_game_renders_until_the_player_quits() -> None:
    output = StringIO()
    commands = iter(["h", "q"])
    game = Game(
        ui=UI(output), input_function=lambda _: next(commands), rng=random.Random(1)
    )

    game.run()

    assert output.getvalue().count("\033[2J\033[H") == 2
    assert "Suggested move:" in output.getvalue()


def test_cli_announces_a_win_after_a_move() -> None:
    output = StringIO()
    commands = iter(["a", "q"])
    board = Board(
        cells=[[1024, 1024, None, None], [None] * 4, [None] * 4, [None] * 4]
    )
    game = Game(board=board, ui=UI(output), input_function=lambda _: next(commands))

    game.run()

    assert game.status is GameStatus.WON
    assert game.board.contains(2048)
    assert "You reached 2048. You win!" in output.getvalue()


def test_cli_announces_game_over_when_no_moves_remain() -> None:
    output = StringIO()
    board = Board(cells=[[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]])
    game = Game(board=board, ui=UI(output), input_function=lambda _: "q")

    game.run()

    assert game.status is GameStatus.LOST
    assert "No moves remain. Game over." in output.getvalue()


def test_about_page_remains_open_until_x_is_pressed() -> None:
    output = StringIO()
    commands = iter(["b", "w", "x", "q"])
    game = Game(ui=UI(output), input_function=lambda _: next(commands))

    game.run()

    rendered = output.getvalue()
    assert "2048, shamelessly ripped off by Jamil Neymatov." in rendered
    assert "No AI was overworked in the making of this game." in rendered
    assert "Press X to return to the game." in rendered
    assert rendered.count("2048 - About") == 2


def test_game_stops_when_input_closes() -> None:
    output = StringIO()

    def closed_input(_: str) -> str:
        raise EOFError

    Game(ui=UI(output), input_function=closed_input).run()

    assert "Score: " in output.getvalue()


def test_default_input_falls_back_to_input_for_non_tty(
    monkeypatch: MonkeyPatch,
) -> None:
    def read_quit(_: str) -> str:
        return "q"

    monkeypatch.setattr("game.game.sys.stdin", SimpleNamespace(isatty=lambda: False))
    monkeypatch.setattr("builtins.input", read_quit)

    output = StringIO()
    Game(ui=UI(output), rng=random.Random(1)).run()

    assert "Score: " in output.getvalue()
