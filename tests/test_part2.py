"""Validation of Part 2 (5x5 Platform Royal, push rule)."""
import unittest

from experiments import part2
from worksheet.agent import ACTIVE, PUSH, REMOVAL, REMOVED, Agent
from worksheet.geometry import RIGHT
from worksheet.patterns import (
    CyclicPattern, EdgePusher, always_left, stationary,
)
from worksheet.worlds import PushWorld

QUIET = lambda *_: None


def pusher_world(victim_cells):
    """One agent at (2,2) always moving right + stationary victims."""
    agents = [Agent("P", "P", CyclicPattern([RIGHT], "right"), (2, 2))]
    for i, cell in enumerate(victim_cells):
        agents.append(Agent(f"V{i}", "V", stationary(), cell))
    return PushWorld(5, 5, agents)


class PushRuleTests(unittest.TestCase):
    def test_push_moves_victim_one_field(self):
        w = pusher_world([(2, 3)])
        w.step()                                   # all enter
        events = w.step()                          # P moves right into V0
        p, v = w.agents
        self.assertEqual(p.position, (2, 3))
        self.assertEqual(v.position, (2, 4))
        self.assertEqual([e.kind for e in events], [PUSH])

    def test_chain_push_throws_last_agent_off(self):
        w = pusher_world([(2, 3), (2, 4)])
        w.step()
        w.step()
        p, v0, v1 = w.agents
        self.assertEqual(v1.status, REMOVED)       # pushed off the grid
        self.assertEqual(v0.position, (2, 4))
        self.assertEqual(p.position, (2, 3))

    def test_walking_off_the_grid_is_permanent(self):
        w = PushWorld(5, 5, [Agent("L", "L", always_left(), (0, 1))])
        w.run(5)
        self.assertEqual(w.agents[0].status, REMOVED)
        self.assertEqual(w.survivors(), [])
        self.assertTrue(any(e.kind == REMOVAL for e in w.events))

    def test_nobody_is_ever_on_the_same_field(self):
        for scn in part2.SCENARIOS:
            w = part2.build_world(scn, with_hunter=True)
            for _ in range(100):
                w.step()
                cells = [a.position for a in w.active_agents()]
                self.assertEqual(len(cells), len(set(cells)))


class ScenarioTests(unittest.TestCase):
    def test_at_least_four_agents_with_distinct_patterns(self):
        w = part2.build_world(part2.SCENARIOS[0])
        self.assertGreaterEqual(len(w.agents), 4)
        labels = {a.pattern.label for a in w.agents}
        self.assertEqual(len(labels), len(w.agents))

    def test_three_runs_with_different_start_states(self):
        starts = [tuple(sorted(s.starts.items())) for s in part2.SCENARIOS]
        self.assertEqual(len(starts), 3)
        self.assertEqual(len(set(starts)), 3)

    def test_runs_are_reproducible(self):
        a = part2.run(out=QUIET, verbose=False)
        b = part2.run(out=QUIET, verbose=False)
        self.assertEqual([r.survivors for r in a], [r.survivors for r in b])

    def test_survivor_count_never_increases(self):
        w = part2.build_world(part2.SCENARIOS[0])
        last = len(w.agents)
        for _ in range(100):
            w.step()
            now = len(w.survivors())
            self.assertLessEqual(now, last)
            last = now

    def test_100_steps_are_simulated(self):
        r = part2.run_scenario(part2.SCENARIOS[0], out=QUIET, verbose=False)
        self.assertEqual(r.world.step_count, 100)


class ChallengeTests(unittest.TestCase):
    def test_hunter_clears_stationary_agents(self):
        agents = [Agent(f"S{i}", "S", stationary(), c)
                  for i, c in enumerate([(1, 1), (1, 3), (3, 1), (3, 3)])]
        agents.append(Agent("Hunter", "H", EdgePusher(), (2, 2)))
        w = PushWorld(5, 5, agents)
        w.run(100)
        self.assertEqual([a.name for a in w.survivors()], ["Hunter"])

    def test_hunter_wins_every_scenario(self):
        for r in part2.run(with_hunter=True, out=QUIET, verbose=False):
            self.assertEqual(r.survivors, ["Hunter"], r.scenario.name)


if __name__ == "__main__":
    unittest.main()
