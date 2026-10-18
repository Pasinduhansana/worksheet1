"""Grid worlds.

GridWorld holds everything the two worlds share (agents, move order, the
step loop, spawning). Subclasses only decide what happens when an agent tries
to move:

    WrapWorld  - edges wrap around, a move into an occupied field is cancelled
    PushWorld  - no walls, a move into an occupied field pushes the occupant
"""
from __future__ import annotations

from typing import Callable, List, Optional, Sequence

from .agent import (
    ACTIVE, BLOCKED, PUSH, REMOVAL, REMOVED, SPAWN_BLOCKED, WAITING, Agent, Event,
)
from .geometry import STAY, Pos, add


class GridWorld:
    def __init__(self, rows: int, cols: int, agents: Sequence[Agent],
                 move_order: Optional[Sequence[str]] = None,
                 retry_blocked: bool = True):
        names = [a.name for a in agents]
        if len(set(names)) != len(names):
            raise ValueError("agent names must be unique")
        self.rows, self.cols = rows, cols
        self.agents: List[Agent] = list(agents)
        for a in self.agents:
            if not self.in_bounds(a.start_pos):
                raise ValueError(f"{a.name}: start {a.start_pos} is outside the grid")

        by_name = {a.name: a for a in self.agents}
        if move_order is None:
            self.move_order = list(self.agents)
        else:
            if sorted(move_order) != sorted(names):
                raise ValueError("move_order must list every agent exactly once")
            self.move_order = [by_name[n] for n in move_order]

        self.retry_blocked = retry_blocked
        self.step_count = 0
        self.events: List[Event] = []

    # ---- queries ---------------------------------------------------------
    def in_bounds(self, pos: Pos) -> bool:
        return 0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols

    def active_agents(self) -> List[Agent]:
        return [a for a in self.agents if a.status == ACTIVE]

    def agent_at(self, pos: Pos) -> Optional[Agent]:
        for a in self.agents:
            if a.status == ACTIVE and a.position == pos:
                return a
        return None

    def survivors(self) -> List[Agent]:
        """Agents still on the grid (or waiting to enter)."""
        return [a for a in self.agents if a.status != REMOVED]

    def snapshot(self) -> tuple:
        return tuple(a.snapshot() for a in self.agents)

    # ---- simulation ------------------------------------------------------
    def step(self) -> List[Event]:
        t = self.step_count
        new_events: List[Event] = []
        # one turn per agent, in the fixed move order
        for agent in self.move_order:
            if agent.status == REMOVED:
                continue
            if agent.status == WAITING:
                if t >= agent.start_time:
                    self._try_spawn(agent, t, new_events)
                continue
            self._move(agent, t, new_events)
        self.step_count += 1
        self.events.extend(new_events)
        return new_events

    def run(self, steps: int,
            on_step: Optional[Callable[["GridWorld", List[Event]], None]] = None) -> None:
        for _ in range(steps):
            events = self.step()
            if on_step:
                on_step(self, events)

    def _try_spawn(self, agent: Agent, t: int, events: List[Event]) -> None:
        occupant = self.agent_at(agent.start_pos)
        if occupant is not None:
            events.append(Event(t, SPAWN_BLOCKED, agent.start_pos,
                                (agent.name, occupant.name)))
            return  # stays WAITING, tries again next step
        agent.position = agent.start_pos
        agent.status = ACTIVE

    def _move(self, agent: Agent, t: int, events: List[Event]) -> None:
        delta = agent.pattern.peek(agent, self)
        if delta == STAY:
            agent.pattern.advance()
            return
        done = self._resolve_move(agent, delta, t, events)
        if done or not self.retry_blocked:
            agent.pattern.advance()

    def _resolve_move(self, agent: Agent, delta: Pos, t: int,
                      events: List[Event]) -> bool:
        """Carry out a move. Return True if the move was consumed."""
        raise NotImplementedError


class WrapWorld(GridWorld):
    """Part 1: torus-shaped world, blocked moves are cancelled."""

    def _resolve_move(self, agent, delta, t, events) -> bool:
        r, c = add(agent.position, delta)
        target = (r % self.rows, c % self.cols)   # % wraps around the edge
        blocker = self.agent_at(target)
        if blocker is not None and blocker is not agent:
            # field is taken -> move is cancelled
            events.append(Event(t, BLOCKED, target, (agent.name, blocker.name)))
            return False
        agent.position = target
        return True


class PushWorld(GridWorld):
    """Part 2: open platform, moving into someone pushes them one field."""

    def _resolve_move(self, agent, delta, t, events) -> bool:
        self._shove(agent, delta, None, t, events)
        return True

    def _shove(self, mover: Agent, delta: Pos, pusher: Optional[Agent],
               t: int, events: List[Event]) -> None:
        origin = mover.position
        target = add(origin, delta)

        if not self.in_bounds(target):
            # walked (or was pushed) off the platform -> out for good
            mover.status = REMOVED
            mover.position = None
            how = ("walked off the grid" if pusher is None
                   else f"was pushed off the grid by {pusher.name}")
            names = (mover.name,) if pusher is None else (mover.name, pusher.name)
            events.append(Event(t, REMOVAL, origin, names, how))
            return

        occupant = self.agent_at(target)
        if occupant is not None:
            # Chain reaction: the occupant is shoved first and makes room.
            self._shove(occupant, delta, mover, t, events)
            where = ("off the grid" if occupant.status == REMOVED
                     else f"to {occupant.position}")
            events.append(Event(t, PUSH, target, (mover.name, occupant.name),
                                f"pushed {where}"))
        mover.position = target
