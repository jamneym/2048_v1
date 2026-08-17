"""Small set of game constants."""

# %% Application constants
APP_NAME: str = "2048"
BOARD_SIZE: int = 4
WINNING_TILE: int = 2048
ABOUT_MESSAGE: str = """2048, shamelessly ripped off by Jamil Neymatov.

Written in Python because life is too short for semicolons.
PEP 8 was consulted. Whether it was followed remains classified.

git blame points exclusively to Jamil Neymatov.
No AI was overworked in the making of this game.

Any bugs are undocumented features.
Any features are accidental.

Works on my machine™."""

# %% Tile generation constants
INITIAL_TILES_MIN: int = 2
INITIAL_TILES_MAX: int = 4
PROBABILITY_OF_FOUR: float = 0.1

# %% Offline AI constants
# The hint system uses expectimax: player moves maximize the evaluated board,
# while tile spawns are evaluated by their 90%/10% expected value. These are
# hand-tuned heuristic weights, not learned machine-learning parameters.
# Number of future random-tile layers considered after the candidate hint move.
AI_SEARCH_DEPTH: int = 3
# Reward per empty cell; open space is the strongest defense against a loss.
AI_EMPTY_CELL_WEIGHT: int = 300
# Reward per equal adjacent pair, which can become a merge on a later move.
AI_MERGE_OPPORTUNITY_WEIGHT: int = 50
# Reward per logarithmic value drop away from the best-aligned board corner.
AI_MONOTONICITY_WEIGHT: int = 20
# Penalty per logarithmic difference between adjacent non-empty tiles.
AI_ROUGHNESS_WEIGHT: int = 10
# Small reward when a largest tile occupies any board corner.
AI_CORNER_WEIGHT: int = 5
# Value returned for a board containing the winning tile, outranking heuristics.
AI_WINNING_BOARD_BONUS: int = 1_000_000
# Magnitude of the negative value returned for a board with no legal moves.
AI_LOST_BOARD_PENALTY: int = 1_000_000
