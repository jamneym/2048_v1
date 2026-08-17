"""Game state orchestration and CLI loop."""

from __future__ import annotations

import random
import sys
from collections.abc import Callable

from game.ai import MoveAdvisor
from game.board import Board
from game.command_parser import CommandParser, CommandType
from game.config import (
    ABOUT_MESSAGE,
    BOARD_SIZE,
    INITIAL_TILES_MAX,
    INITIAL_TILES_MIN,
    PROBABILITY_OF_FOUR,
    WINNING_TILE,
)
from game.models import Direction, GameStatus, MoveResult
from game.tile_generator import TileGenerator
from game.ui import UI

# %% Types
InputFunction = Callable[[str], str]


# %% Game orchestration
class Game:
    """Coordinate board movement, tile generation, and game status."""

    def __init__(
        self,
        board: Board | None = None,
        ui: UI | None = None,
        input_function: InputFunction | None = None,
        rng: random.Random | None = None,
    ) -> None:
        """Create a game, populating a new board with its initial tiles."""
        # Stage 1: Build the collaborators that own board rules, input, and display.
        self.board: Board = board or Board()
        if self.board.size != BOARD_SIZE:
            raise ValueError("Board size must match the configured board size.")
        self._generator: TileGenerator = TileGenerator(
            rng or random.Random(), PROBABILITY_OF_FOUR
        )
        self._advisor: MoveAdvisor = MoveAdvisor()
        self._commands: CommandParser = CommandParser()
        self._hint: str | None = None
        self._showing_about: bool = False
        self.score: int = 0
        self.status: GameStatus = GameStatus.IN_PROGRESS

        # Stage 2: Populate new boards; injected boards retain their layout.
        if board is None:
            for _ in range(self._initial_tile_count()):
                self._generator.place(self.board, value=2)

        # Stage 3: Derive visible state from the starting board and configure I/O.
        self.score = self.board.total()
        self._update_status()
        self._ui: UI = UI() if ui is None else ui
        self._input: InputFunction = (
            self._read_key if input_function is None else input_function
        )

    def move(self, direction: Direction) -> MoveResult:
        """Attempt a move, generating one tile only after a changed board."""
        # Stage 1: Finished games do not accept additional moves.
        if self.status is not GameStatus.IN_PROGRESS:
            return MoveResult(False, 0, self.status)

        # Stage 2: Apply the board rule and determine whether tiles actually moved.
        before = self.board.to_list()
        score_gained = self.board.move(direction)
        changed = self.board.to_list() != before
        if changed:
            # 2048 spawns a tile only after the player made a valid board-changing move.
            self._generator.place(self.board)
            self.score = self.board.total()

        # Stage 3: Recalculate the outcome after the attempted turn.
        self._update_status()
        return MoveResult(changed, score_gained, self.status)

    def suggestion(self) -> Direction | None:
        """Return a local heuristic suggestion without playing the move."""
        return self._advisor.suggest(self.board)

    def restart(self) -> None:
        """Start a new board using the current configuration and generator."""
        # Stage 1: Reset all state that belongs to the previous game.
        self.board = Board()
        self.status = GameStatus.IN_PROGRESS
        self._hint = None
        self._showing_about = False
        # Stage 2: Populate the fresh board using the same random generator.
        for _ in range(self._initial_tile_count()):
            self._generator.place(self.board, value=2)

        # Stage 3: Rebuild score and status from the new board.
        self.score = self.board.total()
        self._update_status()

    def run(self) -> None:
        """Render the board until the player exits or reaches an end state."""
        while True:
            # Stage 1: The About page has its own minimal input mode.
            if self._showing_about:
                self._ui.refresh_about(ABOUT_MESSAGE)
                try:
                    command = self._commands.parse(self._input(""))
                except EOFError:
                    return
                if command.type is CommandType.CLOSE:
                    self._showing_about = False
                continue

            # Stage 2: Render the current game and clear any one-render hint.
            self._ui.refresh(self.board.to_list(), self.score, self.status, self._hint)
            # Hints are transient messages, not part of the game state.
            self._hint = None
            if self.status is not GameStatus.IN_PROGRESS:
                # Stage 3: Ended games permit only restart or exit.
                try:
                    self._ui.message("Press R to restart or Q to quit.")
                    command = self._commands.parse(self._input(""))
                except EOFError:
                    return
                if command.type is CommandType.RESTART:
                    self.restart()
                    continue
                if command.type is CommandType.QUIT:
                    return
                continue

            # Stage 4: Parse an active-game command and dispatch its requested action.
            try:
                self._ui.message(
                    "Move: W/A/S/D   Restart: R   Hint: H   About: B   Quit: Q"
                )
                command = self._commands.parse(self._input(""))
            except EOFError:
                return
            if command.type is CommandType.QUIT:
                return
            if command.type is CommandType.HINT:
                suggestion = self.suggestion()
                self._hint = (
                    f"Suggested move: {suggestion.value.upper()}"
                    if suggestion is not None
                    else "No valid moves remain."
                )
                continue
            if command.type is CommandType.RESTART:
                self.restart()
                continue
            if command.type is CommandType.ABOUT:
                self._showing_about = True
                continue
            if command.type is CommandType.MOVE and command.direction is not None:
                self.move(command.direction)

    @staticmethod
    def _read_key(prompt: str) -> str:
        """Read one console key without waiting for Enter when possible."""
        # Stage 1: Use the platform-specific single-key API on Windows.
        if sys.platform == "win32":
            import msvcrt

            return msvcrt.getwch()

        # Stage 2: Keep redirected input compatible with normal line-based input.
        if not sys.stdin.isatty():
            return input(prompt)

        # Stage 3: Temporarily enable raw terminal mode, then always restore it.
        import termios
        import tty

        if prompt:
            print(prompt, end="", flush=True)
        file_descriptor = sys.stdin.fileno()
        original_settings = termios.tcgetattr(file_descriptor)
        try:
            tty.setraw(file_descriptor)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(file_descriptor, termios.TCSADRAIN, original_settings)

    def _initial_tile_count(self) -> int:
        """Choose how many tiles a newly created board starts with."""
        return self._generator.initial_count(INITIAL_TILES_MIN, INITIAL_TILES_MAX)

    def _update_status(self) -> None:
        """Set the outcome when the board has been won or has no valid moves."""
        # Victory takes precedence over whether any moves remain.
        if self.board.contains(WINNING_TILE):
            self.status = GameStatus.WON
        elif not self.board.available_moves():
            # A full board is still playable when an adjacent pair can merge.
            self.status = GameStatus.LOST
