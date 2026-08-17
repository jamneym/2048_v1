"""Translate player input into game commands."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

from game.models import Direction


# %% Command types
class CommandType(Enum):
    """Actions a player can request from the CLI."""

    MOVE = "move"
    RESTART = "restart"
    HINT = "hint"
    ABOUT = "about"
    CLOSE = "close"
    QUIT = "quit"
    UNKNOWN = "unknown"


# %% Parsed command
@dataclass(frozen=True)
class Command:
    """A parsed player command."""

    type: CommandType
    direction: Direction | None = None


# %% Command parsing
class CommandParser:
    """Parse raw CLI text into commands the game loop can execute."""

    _directions: ClassVar[dict[str, Direction]] = {
        "w": Direction.UP,
        "a": Direction.LEFT,
        "s": Direction.DOWN,
        "d": Direction.RIGHT,
    }

    def parse(self, text: str) -> Command:
        """Normalize player input and map it to one command type."""
        # Stage 1: Make aliases case-insensitive and ignore surrounding space.
        normalized = text.strip().lower()

        # Stage 2: Match commands that do not need a movement direction.
        if normalized in {"q", "quit", "exit"}:
            return Command(CommandType.QUIT)
        if normalized in {"r", "restart"}:
            return Command(CommandType.RESTART)
        if normalized in {"h", "hint"}:
            return Command(CommandType.HINT)
        if normalized in {"b", "about"}:
            return Command(CommandType.ABOUT)
        if normalized == "x":
            return Command(CommandType.CLOSE)

        # Stage 3: Resolve directional keys, or explicitly report unrecognized input.
        direction = self._directions.get(normalized)
        if direction is not None:
            return Command(CommandType.MOVE, direction)
        return Command(CommandType.UNKNOWN)
