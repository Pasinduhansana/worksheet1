"""ASCII rendering of a world."""
from typing import Optional

from .geometry import Pos


def render(world, mark: Optional[Pos] = None) -> str:
    """Draw the grid. Agents show their symbol, '*' marks a special empty field
    (e.g. the red start field), '.' is an empty field."""
    grid = [["." for _ in range(world.cols)] for _ in range(world.rows)]  # empty grid first
    if mark is not None:
        grid[mark[0]][mark[1]] = "*"
    for a in world.active_agents():
        grid[a.position[0]][a.position[1]] = a.symbol
    return "\n".join("  ".join(row) for row in grid)
