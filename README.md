# 2048

A small terminal implementation of 2048 with scoring, win/loss detection, and
an offline AI hint system.

## Play

```powershell
uv run game
```

Use `W`, `A`, `S`, and `D` to move, `R` to restart, `H` for an AI suggested
move, `B` for About, and `Q` to quit.
The Windows CLI reads each key immediately; Enter is not required.
Press `X` to close the About page and return to the game.
Tiles spawn only after a valid move. Reach the configured target tile to win.

The game uses a fixed 4 by 4 board. Constants live in `src/game/config.py`.

## Scoring

Scoring is deliberately simplified: the displayed score is the sum of every
tile currently on the board, recalculated after each valid move and restart.

## AI Hints

`H` runs a local **expectimax** move advisor. It is a game-tree search
algorithm, not an LLM, remote service, or learned neural-network model. It
uses 2048's known movement rules and tile-spawn probabilities to compare the
expected future quality of each legal move. It requires no network connection,
credentials, or additional model files.

The search alternates recursively between two state types:

- A **player state** represents a board before a move. The player controls the
  action, so the advisor keeps the legal move with the highest expected value.
- A **chance state** represents a board immediately after a valid move. 2048
  controls the next tile, so the advisor averages every possible spawn
  outcome using its probability.

```text
Current board
    |
    | Try a candidate move, such as UP
    v
Chance state, depth 3
    |
    | For every empty cell: spawn a 2 (90%) or a 4 (10%)
    v
Player state, depth 2
    |
    | Select the strongest legal continuation
    v
Chance state, depth 2
    |
    | Average every possible next-tile outcome
    v
Player state, depth 1
    |
    | Select the strongest legal continuation
    v
Chance state, depth 1
    |
    | Average every possible next-tile outcome
    v
Leaf board
    |
    | Evaluate board quality, then return values up the tree
    v
Expected value for the original UP move
```

This recursion stops when the configured depth reaches zero or the board has
no legal moves. With `AI_SEARCH_DEPTH = 3`, the advisor evaluates three future
random-tile layers after a candidate move and selects the best continuation
between those layers. Increasing the depth lets the advisor consider more
future consequences, but it also evaluates substantially more board states.

For a chance state with `N` empty cells, each cell is equally likely and its
value is calculated as:

```text
sum for every empty cell:
    (1 / N) * (
        0.90 * value(board with a 2 in that cell)
        + 0.10 * value(board with a 4 in that cell)
    )
```

For a player state, the value is the highest value among its legal moves:

```text
max(value(board after LEFT), value(board after RIGHT),
    value(board after UP), value(board after DOWN))
```

The advisor repeats this calculation for each legal initial direction and
returns the direction with the highest expected value. Every simulation uses a
copy of the board, so requesting a hint never changes the live game. A
per-hint cache also reuses results for repeated board-layout, depth, and
state-type combinations.

At the search boundary, the advisor uses the hand-tuned heuristic weights
below to estimate board quality. They are interpretable configuration values,
not learned machine-learning parameters, and can be adjusted without changing
the search algorithm.

| Setting | Default | How it affects a leaf board |
| --- | ---: | --- |
| `AI_SEARCH_DEPTH` | `3` | Limits the number of future random-tile layers considered after the candidate move. It bounds hint response time. |
| `AI_EMPTY_CELL_WEIGHT` | `300` | Adds `300` for every empty cell. This is the strongest ordinary preference because empty cells preserve room for future moves and tile spawns. |
| `AI_MERGE_OPPORTUNITY_WEIGHT` | `50` | Adds `50` for each horizontally or vertically adjacent equal pair. Such pairs are likely to produce a useful later merge. |
| `AI_MONOTONICITY_WEIGHT` | `20` | Rewards a high-to-low tile gradient away from the best of the four corners. Tile exponents are compared, so each doubling is one step regardless of tile size. |
| `AI_ROUGHNESS_WEIGHT` | `10` | Subtracts `10` times the exponent difference between adjacent non-empty tiles. This discourages scattered large and small tiles that are difficult to merge. |
| `AI_CORNER_WEIGHT` | `5` | Adds `5` when one of the largest tiles is in a corner. It is intentionally a small tie-breaker, not a rule that overrides open space. |
| `AI_WINNING_BOARD_BONUS` | `1,000,000` | Returned immediately when a board contains the target tile, ensuring a winning line outranks normal heuristic differences. |
| `AI_LOST_BOARD_PENALTY` | `1,000,000` | Returned as a negative score when no legal move remains, ensuring the advisor strongly avoids immediate game-over boards. |

Ignoring terminal boards, the leaf score is:

```text
(empty cells * 300)
+ (merge opportunities * 50)
+ (corner-oriented monotonicity * 20)
- (adjacent-tile roughness * 10)
+ (largest tile in a corner * 5)
```

## Setup

```powershell
uv sync
```

## Common Commands

```powershell
uv run ruff check .
uv run ruff format .
uv run pyright
uv run pytest
```

## Layout

```text
src/game/      Board engine, game orchestration, CLI, and AI move advisor
tests/         Test suite
src/game/config.py Small set of game constants
pyproject.toml Project metadata and tool configuration
```
