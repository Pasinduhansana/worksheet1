"""Small unit tests for geometry helpers and pattern objects."""
import unittest

from worksheet.geometry import DOWN, LEFT, RIGHT, STAY, UP, nearest_edge, step_toward
from worksheet.patterns import RandomWalk, clockwise_square


class GeometryTests(unittest.TestCase):
    def test_nearest_edge(self):
        self.assertEqual(nearest_edge((0, 2), 5, 5), (0, UP))
        self.assertEqual(nearest_edge((2, 4), 5, 5), (0, RIGHT))
        self.assertEqual(nearest_edge((2, 1), 5, 5), (1, LEFT))
        # tie (1 step to bottom and to left) -> DOWN wins by definition
        self.assertEqual(nearest_edge((3, 1), 5, 5), (1, DOWN))

    def test_step_toward(self):
        self.assertEqual(step_toward((0, 0), (3, 1)), DOWN)
        self.assertEqual(step_toward((2, 2), (2, 2)), STAY)


class PatternTests(unittest.TestCase):
    def test_clockwise_cycle_length(self):
        self.assertEqual(len(clockwise_square(2).moves), 8)

    def test_random_walk_is_seeded(self):
        def moves(seed):
            p, out = RandomWalk(seed), []
            for _ in range(20):
                out.append(p.peek(None, None))
                p.advance()
            return out
        self.assertEqual(moves(5), moves(5))
        self.assertNotEqual(moves(5), moves(6))


if __name__ == "__main__":
    unittest.main()
