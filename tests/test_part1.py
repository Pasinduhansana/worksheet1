"""Validation of Part 1 (3x3 wrap-around world)."""
import unittest

from experiments import part1
from worksheet.agent import ACTIVE, BLOCKED, WAITING, Agent
from worksheet.analysis import detect_cycle
from worksheet.geometry import RIGHT
from worksheet.patterns import (
    CyclicPattern, always_left, ccw_diamond, clockwise_square, stationary,
)
from worksheet.worlds import WrapWorld


def single(pattern, start=(0, 0)):
    return WrapWorld(3, 3, [Agent("X", "X", pattern, start)])


class PatternTests(unittest.TestCase):
    def test_left_walker_wraps_around(self):
        w = single(always_left())
        w.step()                                   # t=0: enters red field
        self.assertEqual(w.agents[0].position, (0, 0))
        seen = []
        for _ in range(3):
            w.step()
            seen.append(w.agents[0].position)
        self.assertEqual(seen, [(0, 2), (0, 1), (0, 0)])

    def test_clockwise_walks_outer_ring_only(self):
        w = single(clockwise_square(2))
        w.step()
        visited = []
        for _ in range(8):
            w.step()
            visited.append(w.agents[0].position)
        self.assertEqual(visited, [(0, 1), (0, 2), (1, 2), (2, 2),
                                   (2, 1), (2, 0), (1, 0), (0, 0)])
        self.assertNotIn((1, 1), visited)

    def test_diamond_is_counter_clockwise_and_closes(self):
        w = single(ccw_diamond(1))
        w.step()
        visited = []
        for _ in range(4):
            w.step()
            visited.append(w.agents[0].position)
        # down-left, down-right, up-right, up-left (with wrap-around)
        self.assertEqual(visited, [(1, 2), (2, 0), (1, 1), (0, 0)])


class RuleTests(unittest.TestCase):
    def test_blocked_move_is_cancelled_and_logged(self):
        blocker = Agent("B", "B", stationary(), (0, 1))
        mover = Agent("M", "M", CyclicPattern([RIGHT], "right"), (0, 0))
        w = WrapWorld(3, 3, [blocker, mover], move_order=["B", "M"])
        w.step()                                   # both enter
        events = w.step()                          # M tries to enter (0,1)
        self.assertEqual(mover.position, (0, 0))   # did not move
        self.assertEqual([e.kind for e in events], [BLOCKED])
        self.assertEqual(events[0].cell, (0, 1))
        self.assertEqual(events[0].agents, ("M", "B"))

    def test_agents_start_two_steps_apart(self):
        w = part1.build_world()
        status_per_step = []
        for _ in range(6):
            w.step()
            status_per_step.append({a.name: a.status for a in w.agents})
        self.assertEqual(status_per_step[0]["Clockwise"], ACTIVE)
        self.assertEqual(status_per_step[1]["Diamond"], WAITING)
        self.assertEqual(status_per_step[2]["Diamond"], ACTIVE)
        self.assertEqual(status_per_step[3]["Left"], WAITING)
        self.assertEqual(status_per_step[4]["Left"], ACTIVE)

    def test_two_agents_never_share_a_field(self):
        w = part1.build_world()
        for _ in range(200):
            w.step()
            cells = [a.position for a in w.active_agents()]
            self.assertEqual(len(cells), len(set(cells)))

    def test_move_order_changes_outcome(self):
        a = part1.build_world(move_order=["Clockwise", "Diamond", "Left"])
        b = part1.build_world(move_order=["Left", "Diamond", "Clockwise"])
        a.run(50)
        b.run(50)
        self.assertNotEqual([e.step for e in a.events], [e.step for e in b.events])


class SimulationTests(unittest.TestCase):
    def test_run_50_steps_is_deterministic(self):
        quiet = lambda *_: None
        r1 = part1.run(50, out=quiet)
        r2 = part1.run(50, out=quiet)
        self.assertEqual(r1.world.events, r2.world.events)
        self.assertGreater(len(r1.conflicts), 0)

    def test_world_state_becomes_periodic(self):
        r = part1.run(50, out=lambda *_: None)
        self.assertIsNotNone(r.cycle)
        first, period = r.cycle
        self.assertEqual(r.history[first], r.history[first + period])

    def test_detect_cycle_helper(self):
        self.assertEqual(detect_cycle([1, 2, 3, 2, 3, 2]), (1, 2))
        self.assertIsNone(detect_cycle([1, 2, 3]))


if __name__ == "__main__":
    unittest.main()
