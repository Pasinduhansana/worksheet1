"""Small grid-geometry helpers.

Positions are (row, col). Row 0 is the TOP row, col 0 is the LEFT column.
A move is a (d_row, d_col) delta.
"""
from typing import Tuple

Pos = Tuple[int, int]

STAY: Pos = (0, 0)
UP: Pos = (-1, 0)
DOWN: Pos = (1, 0)
LEFT: Pos = (0, -1)
RIGHT: Pos = (0, 1)
UP_LEFT: Pos = (-1, -1)
UP_RIGHT: Pos = (-1, 1)
DOWN_LEFT: Pos = (1, -1)
DOWN_RIGHT: Pos = (1, 1)


def add(pos: Pos, delta: Pos) -> Pos:
    return (pos[0] + delta[0], pos[1] + delta[1])


def manhattan(a: Pos, b: Pos) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def nearest_edge(pos: Pos, rows: int, cols: int) -> Tuple[int, Pos]:
    """Return (distance, direction) to the closest edge of the grid.

    Distance 0 means the cell lies ON that edge, so one more step in
    `direction` leaves the grid. Ties are broken in the order UP, DOWN, LEFT, RIGHT.
    """
    r, c = pos
    candidates = [
        (r, UP),
        (rows - 1 - r, DOWN),
        (c, LEFT),
        (cols - 1 - c, RIGHT),
    ]
    return min(candidates, key=lambda item: item[0])


def step_toward(src: Pos, dst: Pos) -> Pos:
    """One orthogonal step from src towards dst (largest gap first, rows win ties)."""
    dr, dc = dst[0] - src[0], dst[1] - src[1]
    if dr == 0 and dc == 0:
        return STAY
    if abs(dr) >= abs(dc):
        return (1 if dr > 0 else -1, 0)
    return (0, 1 if dc > 0 else -1)
