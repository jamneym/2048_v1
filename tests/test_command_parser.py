from game.command_parser import CommandParser, CommandType
from game.models import Direction


def test_parse_move_keys() -> None:
    parser = CommandParser()

    assert parser.parse("w").direction is Direction.UP
    assert parser.parse("a").direction is Direction.LEFT
    assert parser.parse("s").direction is Direction.DOWN
    assert parser.parse("d").direction is Direction.RIGHT


def test_parse_named_commands() -> None:
    parser = CommandParser()

    assert parser.parse("q").type is CommandType.QUIT
    assert parser.parse("quit").type is CommandType.QUIT
    assert parser.parse("restart").type is CommandType.RESTART
    assert parser.parse("hint").type is CommandType.HINT
    assert parser.parse("about").type is CommandType.ABOUT
    assert parser.parse("x").type is CommandType.CLOSE


def test_parse_normalizes_input_and_rejects_unknown_commands() -> None:
    parser = CommandParser()

    assert parser.parse(" H ").type is CommandType.HINT
    assert parser.parse("nope").type is CommandType.UNKNOWN
