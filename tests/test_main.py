from unittest.mock import patch

from game.main import main


def test_main_launches_the_game_loop() -> None:
    with patch("game.main.Game") as game:
        main()

    game.assert_called_once_with()
    game.return_value.run.assert_called_once_with()
