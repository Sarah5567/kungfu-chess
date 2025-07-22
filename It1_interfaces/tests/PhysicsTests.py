import unittest
from unittest.mock import Mock
from Physics import IdlePhysics, MovePhysics, JumpPhysics, ShortRestPhysics, LongRestPhysics
from Command import Command


class TestPhysics(unittest.TestCase):

    def setUp(self):
        self.board = Mock()
        self.board.cell_to_world.side_effect = lambda cell: (cell[0] * 1.0, cell[1] * 1.0)
        self.board.algebraic_to_cell.side_effect = lambda s: (ord(s[0]) - ord('a'), int(s[1]) - 1)

    def test_idle_physics(self):
        p = IdlePhysics((0, 0), self.board)
        cmd = Command(0, "P1", "idle", [])
        p.reset(cmd)
        self.assertTrue(p.can_be_captured())
        self.assertTrue(p.can_capture())
        self.assertIsNone(p.update(100))
        self.assertEqual(p.get_pos(), (0.0, 0.0))

    def test_move_physics_full_move(self):
        p = MovePhysics((0, 0), self.board, speed_m_s=1.0)
        cmd = Command(0, "P1", "move", ["a1", "a3"])
        p.reset(cmd)
        # simulate passage of time: movement should take 2 meters / 1m/s = 2s = 2000ms
        result = p.update(0)  # should return Wait command
        self.assertEqual(result.type, "Wait")
        result = p.update(2000)
        self.assertEqual(result, cmd)
        self.assertEqual(p.get_pos(), (0.0, 2.0))
        self.assertTrue(p.can_be_captured())
        self.assertTrue(p.can_capture())

    def test_move_physics_partial(self):
        p = MovePhysics((0, 0), self.board, speed_m_s=1.0)
        cmd = Command(0, "P1", "move", ["a1", "a3"])
        p.reset(cmd)
        p.update(0)
        result = p.update(1000)  # halfway
        self.assertEqual(result.type, "Wait")
        pos = p.get_pos()
        self.assertAlmostEqual(pos[0], 0.0)
        self.assertAlmostEqual(pos[1], 1.0, delta=0.01)

    def test_jump_physics(self):
        p = JumpPhysics((0, 0), self.board)
        cmd = Command(0, "P1", "jump", [])
        p.reset(cmd)
        self.assertFalse(p.can_be_captured())
        self.assertFalse(p.can_capture())
        self.assertIsNone(p.update(0))
        self.assertEqual(p.update(1000), cmd)

    def test_short_rest_physics(self):
        p = ShortRestPhysics((0, 0), self.board)
        cmd = Command(0, "P1", "short_rest", [])
        p.reset(cmd)
        self.assertTrue(p.can_be_captured())
        self.assertFalse(p.can_capture())
        self.assertIsNone(p.update(0))
        self.assertEqual(p.update(500), cmd)

    def test_long_rest_physics(self):
        p = LongRestPhysics((0, 0), self.board)
        cmd = Command(0, "P1", "long_rest", [])
        p.reset(cmd)
        self.assertTrue(p.can_be_captured())
        self.assertFalse(p.can_capture())
        self.assertIsNone(p.update(0))
        self.assertEqual(p.update(1500), cmd)


if __name__ == '__main__':
    unittest.main()
