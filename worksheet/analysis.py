"""Helpers that turn raw events/state history into something readable."""
from collections import Counter
from typing import Dict, Hashable, List, Optional, Sequence, Tuple

from .agent import BLOCKED, SPAWN_BLOCKED, Event


def conflicts_only(events: Sequence[Event]) -> List[Event]:
    return [e for e in events if e.kind in (BLOCKED, SPAWN_BLOCKED)]


def summarize_conflicts(events: Sequence[Event]) -> dict:
    conflicts = conflicts_only(events)
    return {
        "total": len(conflicts),
        "by_cell": Counter(e.cell for e in conflicts),
        "by_pair": Counter((e.agents[0], e.agents[1]) for e in conflicts),
        "steps": [e.step for e in conflicts],
    }


def detect_cycle(states: Sequence[Hashable]) -> Optional[Tuple[int, int]]:
    """Find the first repeated state in a history.

    Returns (index_of_first_occurrence, period) or None. A deterministic
    system with finitely many states must eventually repeat forever, so a
    repeated state proves the conflict pattern is periodic.
    """
    seen: Dict[Hashable, int] = {}
    for i, s in enumerate(states):
        if s in seen:               # same state again -> we have a cycle
            return seen[s], i - seen[s]
        seen[s] = i
    return None
