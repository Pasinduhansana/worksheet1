"""Agent and Event data classes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, TYPE_CHECKING

from .geometry import Pos

if TYPE_CHECKING:  # avoid a circular import at runtime
    from .patterns import MovementPattern

# Agent life-cycle
WAITING = "waiting"   # has not entered the world yet (start_time not reached)
ACTIVE = "active"     # on the grid
REMOVED = "removed"   # left the grid for good

# Event kinds
SPAWN_BLOCKED = "spawn_blocked"
BLOCKED = "blocked"
PUSH = "push"
REMOVAL = "removal"


@dataclass
class Agent:
    name: str
    symbol: str                 # single character used in the ASCII display
    pattern: "MovementPattern"
    start_pos: Pos
    start_time: int = 0
    position: Optional[Pos] = None
    status: str = WAITING

    @property
    def is_active(self) -> bool:
        return self.status == ACTIVE

    def snapshot(self) -> tuple:
        """Hashable description of everything that determines the future."""
        return (self.name, self.status, self.position, self.pattern.state())


@dataclass(frozen=True)
class Event:
    """Something worth logging that happened during one time-step."""
    step: int
    kind: str
    cell: Pos
    agents: Tuple[str, ...]
    detail: str = ""

    def describe(self) -> str:
        t = f"t={self.step:03d}"
        a = self.agents[0]
        b = self.agents[1] if len(self.agents) > 1 else ""
        if self.kind == BLOCKED:
            return (f"{t}  CONFLICT at field {self.cell}: {a} tried to enter, "
                    f"but {b} is there -> move cancelled")
        if self.kind == SPAWN_BLOCKED:
            return (f"{t}  CONFLICT at field {self.cell}: {a} wanted to start here, "
                    f"but {b} is standing on it -> start delayed")
        if self.kind == PUSH:
            return f"{t}  PUSH at field {self.cell}: {a} pushed {b} ({self.detail})"
        if self.kind == REMOVAL:
            return f"{t}  OUT from field {self.cell}: {a} {self.detail}"
        return f"{t}  {self.kind} {self.cell} {self.agents} {self.detail}"
