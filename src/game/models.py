"""Shared enums and result types for the game engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# %% Direction types
class Direction(Enum):
    """A direction in which tiles can move."""

    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


# %% Game status
class GameStatus(Enum):
    """The current outcome of a game."""

    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


# %% Move results
@dataclass(frozen=True)
class MoveResult:
    """The observable result of attempting one move."""

    changed: bool
    score_gained: int
    status: GameStatus
