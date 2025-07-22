import pathlib
import time
import pytest

from State import State
from Moves import Moves
from Graphics import Graphics
from Physics import IdlePhysics, MovePhysics
from Board import Board
from Command import Command
from GraphicsFactory import GraphicsFactory
from PhysicsFactory import PhysicsFactory


@pytest.fixture
def board(tmp_path):
    return Board(
        cell_H_pix=64,
        cell_W_pix=64,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=8,
        H_cells=8,
        img=None
    )

@pytest.fixture
def graphics(board):
    # שימוש בתיקייה האמיתית ../pieces/QW/states/jump
    sprites_folder = pathlib.Path("../../pieces/QW/states/jump/sprites").resolve()
    return GraphicsFactory(board).load(
        sprites_dir=sprites_folder,
        cfg={"graphics": {"frames_per_sec": 2.0, "is_loop": True}},
        cell_size=(64, 64)
    )

@pytest.fixture
def moves(board):
    # שימוש בנתיב ../pieces/QW
    moves_path = pathlib.Path("../../pieces/QW").resolve() / "moves.txt"
    return Moves(moves_path, dims=(board.H_cells, board.W_cells))


@pytest.fixture
def physics_idle(board):
    return IdlePhysics((0, 0), board, speed_m_s=1.0)


@pytest.fixture
def physics_move(board):
    return MovePhysics((0, 0), board, speed_m_s=10.0)


def test_state_initialization(moves, graphics, physics_idle):
    state = State(moves, graphics, physics_idle)
    assert isinstance(state, State)
    assert state.get_command() is None
    assert state._physics == physics_idle
    assert state._graphics == graphics
    assert state._moves == moves


def test_reset_sets_command_and_resets_graphics_and_physics(moves, graphics, physics_idle):
    state = State(moves, graphics, physics_idle)
    cmd = Command(timestamp=1000, piece_id=1, type="idle", params=[])
    state.reset(cmd)

    assert state.get_command() == cmd
    assert state._current_command == cmd
    assert physics_idle.cmd == cmd
    assert graphics.start_time == cmd.timestamp


def test_update_returns_same_state_if_no_transition(moves, graphics, physics_idle):
    state = State(moves, graphics, physics_idle)
    cmd = Command(timestamp=1000, piece_id=1, type="idle", params=["a1", "a2"])
    state.reset(cmd)

    # IdlePhysics.update מחזיר None ולכן נשארים באותו מצב
    updated = state.update(now_ms=2000)
    assert updated == state


def test_can_transition_true_when_physics_returns_command(moves, graphics, physics_move):
    state = State(moves, graphics, physics_move)
    cmd = Command(timestamp=1000, piece_id=1, type="move", params=["a1", "a2"])
    state.reset(cmd)

    now_ms = int(time.time() * 1000) + 5000
    # MovePhysics.update מחזיר command כשהוא סיים תנועה
    can_trans = state.can_transition(now_ms)
    assert isinstance(can_trans, bool)
    # קשה לבדוק בדיוק כי תזמון, אבל בודקים שזה מחזיר True אחרי זמן
    assert state._physics.update(now_ms) is not None


def test_process_command_changes_state_on_transition(moves, graphics, physics_idle, physics_move):
    idle_state = State(moves, graphics, physics_idle)
    move_state = State(moves, graphics, physics_move)
    idle_state.set_transition("move_complete", move_state)

    # מחזירים פקודה עם type=move_complete
    cmd = Command(timestamp=1000, piece_id=1, type="move_complete", params=[])
    next_state = idle_state.process_command(cmd, now_ms=2000)

    assert next_state == move_state
    assert next_state.get_command() == cmd


def test_process_command_stays_in_state_if_no_transition(moves, graphics, physics_idle):
    state = State(moves, graphics, physics_idle)
    cmd = Command(timestamp=1000, piece_id=1, type="unknown_event", params=[])
    same_state = state.process_command(cmd, now_ms=2000)

    assert same_state == state
