"""Part 1 - Basic interactions: 3x3 wrap-around world, 3 agents.

Rules implemented
  * leaving one side re-enters on the opposite side (WrapWorld)
  * each agent has its own movement pattern
  * a move into an occupied field is cancelled (the agent stays where it is)
  * all agents start on the red field, START_GAP time-steps apart
  * the order in which agents move each round is configurable
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence

from worksheet.agent import ACTIVE, Agent, Event
from worksheet.analysis import conflicts_only, detect_cycle, summarize_conflicts
from worksheet.patterns import always_left, ccw_diamond, clockwise_square
from worksheet.render import render
from worksheet.worlds import WrapWorld

GRID_SIZE = 3
RED_FIELD = (0, 0)      # (row, col) - top-left corner
START_GAP = 2           # time-steps between consecutive agents entering

# name -> (display symbol, pattern factory)
AGENT_SPECS = {
    "Clockwise": ("C", lambda: clockwise_square(2)),
    "Diamond":   ("D", lambda: ccw_diamond(1)),
    "Left":      ("L", always_left),
}
DEFAULT_ORDER = ("Clockwise", "Diamond", "Left")


def build_world(start_order: Sequence[str] = DEFAULT_ORDER,
                move_order: Optional[Sequence[str]] = None,
                retry_blocked: bool = False) -> WrapWorld:
    """start_order: who enters first/second/third (t = 0, 2, 4).
    move_order:  who moves first within a round (defaults to DEFAULT_ORDER)."""
    agents = []
    for i, name in enumerate(start_order):
        symbol, factory = AGENT_SPECS[name]
        agents.append(Agent(name, symbol, factory(), RED_FIELD,
                            start_time=i * START_GAP))
    return WrapWorld(GRID_SIZE, GRID_SIZE, agents,
                     move_order=list(move_order or DEFAULT_ORDER),
                     retry_blocked=retry_blocked)


@dataclass
class Part1Result:
    world: WrapWorld
    conflicts: List[Event]
    history: List[tuple]
    cycle: Optional[tuple]


def run(steps: int = 50,
        start_order: Sequence[str] = DEFAULT_ORDER,
        move_order: Optional[Sequence[str]] = None,
        retry_blocked: bool = False,
        show: bool = False,
        out: Callable[[str], None] = print) -> Part1Result:
    world = build_world(start_order, move_order, retry_blocked)
    history: List[tuple] = []

    out("=" * 70)
    out("PART 1 - 3x3 wrap-around world, 3 agents")
    out(f"  start order (t=0,2,4): {' -> '.join(start_order)}")
    out(f"  move order each round: {' -> '.join(a.name for a in world.move_order)}")
    out(f"  blocked agents: {'wait and retry the same move (can deadlock!)' if retry_blocked else 'cancelled move is lost, pattern continues'}")
    out(f"  steps: {steps}   red field: {RED_FIELD} (shown as '*')   (row, col), (0,0) = top-left")
    out("=" * 70)

    def on_step(w: WrapWorld, events: List[Event]) -> None:
        history.append(w.snapshot())
        if show:
            out(f"\n-- after step t={w.step_count - 1:03d} --")
            out(render(w, mark=RED_FIELD))
        for e in conflicts_only(events):
            out(e.describe())

    world.run(steps, on_step)

    summary = summarize_conflicts(world.events)
    cycle = detect_cycle(history)

    out("\n" + "-" * 70)
    out(f"SUMMARY: {summary['total']} conflicts in {steps} steps")
    out("  by field:")
    for cell, n in sorted(summary["by_cell"].items(), key=lambda kv: (-kv[1], kv[0])):
        out(f"    {cell}: {n}")
    out("  by (mover blocked by blocker):")
    for (a, b), n in sorted(summary["by_pair"].items(), key=lambda kv: (-kv[1], kv[0])):
        out(f"    {a} blocked by {b}: {n}")
    if summary["steps"]:
        out(f"  conflict time-steps: {summary['steps']}")
    if cycle:
        first, period = cycle
        out(f"  PATTERN: the whole world state first repeats after step {first} "
            f"with period {period}.")
        out(f"  -> from step {first} on, the same {period}-step sequence of moves "
            f"(and conflicts) repeats forever.")
        in_cycle = [e for e in conflicts_only(world.events)
                    if first < e.step <= first + period]
        out(f"  Inside ONE period there are {len(in_cycle)} conflict(s):")
        for e in in_cycle:
            out(f"    t={e.step:03d} (cycle step {e.step - first}) at {e.cell}: "
                f"{e.agents[0]} blocked by {e.agents[1]}")
    else:
        out("  No repeated world state found in this many steps - try more steps.")
    out("-" * 70)
    return Part1Result(world, conflicts_only(world.events), history, cycle)
