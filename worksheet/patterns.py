"""Movement patterns (the 'brain' of each agent).

A pattern has two jobs:
    peek(agent, world)  -> the (d_row, d_col) the agent WANTS to make next
    advance()           -> consume that move (called by the world)
Splitting the two lets a world decide whether a blocked agent retries the
same move or loses it.
"""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Sequence

from .geometry import (
    DOWN, DOWN_LEFT, DOWN_RIGHT, LEFT, RIGHT, STAY, UP, UP_LEFT, UP_RIGHT,
    Pos, manhattan, nearest_edge, step_toward,
)


class MovementPattern(ABC):
    label = "pattern"

    @abstractmethod
    def peek(self, agent, world) -> Pos:
        """Return the move the agent wants to make, without consuming it."""

    def advance(self) -> None:
        """Consume the current move."""

    def state(self):
        """Hashable internal state (used for cycle detection)."""
        return None


class CyclicPattern(MovementPattern):
    """Repeats a fixed list of moves forever."""

    def __init__(self, moves: Sequence[Pos], label: str):
        self.moves = tuple(moves)
        self.label = label
        self._i = 0

    def peek(self, agent, world) -> Pos:
        return self.moves[self._i]

    def advance(self) -> None:
        self._i = (self._i + 1) % len(self.moves)

    def state(self):
        return self._i


# --------------------------------------------------------------------------
# Factories for the patterns required by the worksheet
# --------------------------------------------------------------------------
def clockwise_square(side: int = 2) -> CyclicPattern:
    """Walk clockwise around a square with the given side length.

    side=2 on a 3x3 grid, started in the top-left corner, walks the whole
    outer ring (8 moves): right, right, down, down, left, left, up, up.
    """
    moves = [RIGHT] * side + [DOWN] * side + [LEFT] * side + [UP] * side
    return CyclicPattern(moves, f"clockwise square (side {side})")


def ccw_diamond(radius: int = 1) -> CyclicPattern:
    """Diagonal moves tracing a diamond counter-clockwise.

    top -> left -> bottom -> right -> top, i.e.
    down-left, down-right, up-right, up-left (each repeated `radius` times).
    """
    moves = [DOWN_LEFT] * radius + [DOWN_RIGHT] * radius + \
            [UP_RIGHT] * radius + [UP_LEFT] * radius
    return CyclicPattern(moves, f"counter-clockwise diamond (radius {radius})")


def always_left() -> CyclicPattern:
    return CyclicPattern([LEFT], "always left")


def stationary() -> CyclicPattern:
    return CyclicPattern([STAY], "stationary")


# --------------------------------------------------------------------------
# Other behaviours
# --------------------------------------------------------------------------
class RandomWalk(MovementPattern):
    """Random orthogonal steps. Seeded, so every run is reproducible."""
    label = "random walk"
    _CHOICES = (UP, DOWN, LEFT, RIGHT)

    def __init__(self, seed: int):
        self._rng = random.Random(seed)
        self._next = self._rng.choice(self._CHOICES)

    def peek(self, agent, world) -> Pos:
        return self._next

    def advance(self) -> None:
        self._next = self._rng.choice(self._CHOICES)


class EdgePusher(MovementPattern):
    """CHALLENGE agent - intentionally antagonistic.

    New capabilities compared with the 'blind' agents:
      * it SEES every other agent on the platform, and
      * it can READ each victim's pending move (victim.pattern.peek), so it
        knows where a victim will be the next time the hunter acts.

    Strategy, re-evaluated every step (no memory needed):
      1. PUSH NOW   if it already stands directly behind some victim, i.e.
                    on the opposite side from that victim's nearest edge.
                    The push shoves the victim one field towards the edge
                    (and off the grid once the victim is on the edge).
      2. Otherwise  pick the victim closest to an edge (ignoring victims that
                    are about to walk off by themselves), predict where it
                    will stand next, and walk to the 'stand' cell behind that
                    predicted position. If already there, wait.
    The pusher always moves INTO a cell that is on the grid, so its own push
    can never throw it off the platform.
    """
    label = "edge pusher (hunter)"

    @staticmethod
    def _stand(pos: Pos, world):
        dist, d = nearest_edge(pos, world.rows, world.cols)
        return (pos[0] - d[0], pos[1] - d[1]), d, dist

    def peek(self, agent, world) -> Pos:
        victims = [a for a in world.active_agents() if a is not agent]
        if not victims:
            return STAY

        # 1) can I push somebody right now?
        for v in sorted(victims, key=lambda a: (self._stand(a.position, world)[2], a.name)):
            stand, d, _ = self._stand(v.position, world)
            if agent.position == stand:
                return d

        # 2) predict where each victim will be next time I act
        candidates = []
        for v in victims:
            nxt = (v.position[0] + v.pattern.peek(v, world)[0],
                   v.position[1] + v.pattern.peek(v, world)[1])
            if not world.in_bounds(nxt):
                continue                      # it will leave on its own
            stand, _, dist = self._stand(nxt, world)
            candidates.append((dist, manhattan(agent.position, stand), v.name, stand))
        if not candidates:
            return STAY
        stand = min(candidates)[3]
        if agent.position == stand:
            return STAY
        return step_toward(agent.position, stand)
