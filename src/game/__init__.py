"""Core package for the 2048 project."""

from game.ai import MoveAdvisor
from game.board import Board
from game.command_parser import Command, CommandParser, CommandType
from game.config import ABOUT_MESSAGE, APP_NAME, BOARD_SIZE, WINNING_TILE
from game.game import Game
from game.models import Direction, GameStatus, MoveResult
from game.tile_generator import TileGenerator
from game.ui import UI, Cell

# %% Public API
__all__ = [
    "ABOUT_MESSAGE",
    "APP_NAME",
    "BOARD_SIZE",
    "UI",
    "WINNING_TILE",
    "Board",
    "Cell",
    "Command",
    "CommandParser",
    "CommandType",
    "Direction",
    "Game",
    "GameStatus",
    "MoveAdvisor",
    "MoveResult",
    "TileGenerator",
]
