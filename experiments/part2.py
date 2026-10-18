"""Part 2 - Platform Royal: 5x5 open platform, agents push each other.

Rules implemented
  * no walls; an agent that leaves the grid is gone for good
  * moving into an occupied field pushes the occupant one field (chains too)
  * 4 agents with different movement patterns + optional 5th 'Hunter' (challenge)
  * 3 scenarios with different start states / move orders, 100 steps each
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from worksheet.agent import PUSH, REMOVAL, Agent, Event
from worksheet.geometry import Pos
from worksheet.patterns import (
    EdgePusher, RandomWalk, always_left, ccw_diamond, clockwise_square,
)
from worksheet.render import render
from worksheet.worlds import PushWorld

GRID_SIZE = 5
STEPS = 100


@dataclass(frozen=True)
class Scenario:
    name: str
    starts: Dict[str, Pos]          # agent name -> start field
    order: Tuple[str, ...]          # move order within a round
    seed: int = 1                   # seed for the random walker


SCENARIOS: List[Scenario] = [
    # 3 runs, each with different start fields and a different move order
    Scenario("Run 1",
             starts={"Clockwise": (1, 1), "Diamond": (1, 3), "Left": (3, 3),
                     "Random": (3, 1), "Hunter": (2, 2)},
             order=("Clockwise", "Diamond", "Left", "Random", "Hunter"),
             seed=1),
    Scenario("Run 2",
             starts={"Clockwise": (0, 0), "Diamond": (2, 2), "Left": (4, 4),
                     "Random": (1, 3), "Hunter": (3, 1)},
             order=("Random", "Left", "Diamond", "Clockwise", "Hunter"),
             seed=2),
    Scenario("Run 3",
             starts={"Clockwise": (3, 3), "Diamond": (1, 1), "Left": (2, 4),
                     "Random": (4, 2), "Hunter": (0, 2)},
             order=("Left", "Clockwise", "Random", "Diamond", "Hunter"),
             seed=3),
]


def build_world(scn: Scenario, with_hunter: bool = False) -> PushWorld:
    agents = [
        Agent("Clockwise", "C", clockwise_square(2), scn.starts["Clockwise"]),
        Agent("Diamond",   "D", ccw_diamond(1),      scn.starts["Diamond"]),
        Agent("Left",      "L", always_left(),       scn.starts["Left"]),
        Agent("Random",    "R", RandomWalk(scn.seed), scn.starts["Random"]),
    ]
    order = [n for n in scn.order if n != "Hunter"]
    if with_hunter:     # only used for the optional challenge
        agents.append(Agent("Hunter", "H", EdgePusher(), scn.starts["Hunter"]))
        order = list(scn.order)
    return PushWorld(GRID_SIZE, GRID_SIZE, agents, move_order=order)


@dataclass
class RunResult:
    scenario: Scenario
    world: PushWorld
    survivors: List[str]

    @property
    def count(self) -> int:
        return len(self.survivors)


def run_scenario(scn: Scenario, steps: int = STEPS, with_hunter: bool = False,
                 show: bool = False, verbose: bool = True,
                 out: Callable[[str], None] = print) -> RunResult:
    world = build_world(scn, with_hunter)
    out("=" * 70)
    out(f"{scn.name}: starts = {{ " +
        ", ".join(f"{a.name}{a.start_pos}" for a in world.agents) + " }")
    out(f"  move order: {' -> '.join(a.name for a in world.move_order)}")
    def on_step(w: PushWorld, events: List[Event]) -> None:
        if show:
            out(f"\n-- after step t={w.step_count - 1:03d} --\n{render(w)}")
        if verbose:
            for e in events:
                out("  " + e.describe())

    world.run(steps, on_step)
    # everyone still on the platform counts as a survivor
    survivors = [a.name for a in world.survivors()]
    out(f"  RESULT after {steps} steps: {len(survivors)} agent(s) remain "
        f"-> {survivors if survivors else 'nobody'}")
    return RunResult(scn, world, survivors)


def run(steps: int = STEPS, with_hunter: bool = False, show: bool = False,
        verbose: bool = True,
        out: Callable[[str], None] = print) -> List[RunResult]:
    out("PART 2 - Platform Royal (5x5, push rule)"
        + ("  [with challenge agent 'Hunter']" if with_hunter else ""))
    results = [run_scenario(s, steps, with_hunter, show, verbose, out)
               for s in SCENARIOS]
    out("\n" + "-" * 70)
    out("SURVIVORS TABLE")
    out(f"  {'run':<8}{'agents at start':<18}{'remaining':<11}who")
    for r in results:
        out(f"  {r.scenario.name:<8}{len(r.world.agents):<18}{r.count:<11}"
            f"{', '.join(r.survivors) or 'nobody'}")
    out("-" * 70)
    return results
