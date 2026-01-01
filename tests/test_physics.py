from unittest.mock import MagicMock
from Physics import IdlePhysics, MovePhysics, JumpPhysics, ShortRestPhysics, LongRestPhysics
from Command import Command


def mock_board():
    board = MagicMock()
    board.cell_to_world.side_effect = lambda cell: (cell[1] * 1.0, cell[0] * 1.0)
    board.world_to_cell.side_effect = lambda pos: (int(pos[1]), int(pos[0]))
    board.algebraic_to_cell.side_effect = lambda alg: {
        "a1": (0, 0), "a2": (0, 1), "a3": (2, 0), "b2": (1, 1), "c3": (2, 2), "e5": (4, 4)
    }[alg]
    return board


def test_idle_physics():
    board = mock_board()
    phys = IdlePhysics((2, 3), board)
    cmd = Command(0, "P", "idle", [(2, 3)])
    phys.reset(cmd)
    assert phys.get_pos_in_cell() == (2, 3)
    assert phys.can_capture()
    assert phys.can_be_captured()
    assert phys.update(1234) is None


def test_move_physics():
    board = mock_board()
    phys = MovePhysics((0, 0), board, speed_m_s=1.0)
    cmd = Command(0, "PB", "move", ["a2", "a3"])
    phys.reset(cmd)

    assert not phys.finished
    assert phys.update(500) is None
    assert not phys.finished
    assert phys.update(phys.duration_ms + phys.extra_delay_ms + 499) is None
    assert phys.update(phys.duration_ms + phys.extra_delay_ms + 500) is None

    assert phys.finished
    assert phys.get_pos_in_cell() == (2, 0)


def test_jump_physics():
    board = mock_board()
    phys = JumpPhysics((1, 1), board)
    cmd = Command(0, "P", "jump", ["b2", "c3"])
    phys.reset(cmd)

    assert not phys.finished
    assert phys.update(500) is None
    assert not phys.finished
    phys.update(1600)
    assert phys.finished
    assert not phys.can_be_captured()
    assert not phys.can_capture()


def test_short_rest_physics():
    board = mock_board()
    phys = ShortRestPhysics((2, 2), board)
    cmd = Command(0, "P", "rest", [(2, 2)])
    phys.reset(cmd)

    assert not phys.finished
    phys.update(100)
    assert not phys.finished
    phys.update(600)
    assert phys.finished
    assert phys.can_be_captured()
    assert not phys.can_capture()


def test_long_rest_physics():
    board = mock_board()
    phys = LongRestPhysics((4, 4), board)
    cmd = Command(0, "P", "rest", [(4, 4)])
    phys.reset(cmd)

    assert not phys.finished
    phys.update(100)
    assert not phys.finished
    phys.update(1600)
    assert phys.finished
    assert phys.can_be_captured()
    assert not phys.can_capture()
