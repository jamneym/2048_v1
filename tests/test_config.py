from game.config import (
    ABOUT_MESSAGE,
    BOARD_SIZE,
    INITIAL_TILES_MAX,
    INITIAL_TILES_MIN,
    WINNING_TILE,
)


def test_config_defines_the_game_defaults() -> None:
    assert BOARD_SIZE == 4
    assert WINNING_TILE == 2048
    assert INITIAL_TILES_MIN == 2
    assert INITIAL_TILES_MAX == 4
    assert "Jamil Neymatov" in ABOUT_MESSAGE
