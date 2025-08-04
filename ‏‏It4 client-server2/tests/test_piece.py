import pytest
from unittest.mock import MagicMock
from Piece import Piece
from Command import Command
from State import State


def make_mock_state(name="idle", transitions=None, physics=None, graphics=None, moves=None):
    physics = physics or MagicMock()
    graphics = graphics or MagicMock()
    state = State(moves=moves, graphics=graphics, physics=physics)
    state.name = name
    state.transitions = transitions or {}
    state.is_command_possible = MagicMock(return_value=True)
    state.process_command = MagicMock(side_effect=lambda cmd: transitions.get(cmd.type, state))
    return state



def test_on_command_executes_valid_command_and_transitions():
    next_state = make_mock_state("move")
    current_state = make_mock_state("idle", transitions={"move": next_state})

    piece = Piece("PW_1", current_state)
    cmd = Command(100, "PW_1", "move", [(4, 4), (4, 5)])

    piece.on_command(cmd, now_ms=100, dst_empty=True)

    current_state.is_command_possible.assert_called_once_with(cmd)
    next_state = current_state.process_command.return_value
    assert piece._state == next_state
    assert piece._current_cmd == cmd


def test_on_command_rejects_invalid_command():
    state = make_mock_state("idle")
    state.is_command_possible.return_value = False
    piece = Piece("PW_1", state)
    cmd = Command(100, "PW_1", "move", [(4, 4), (4, 5)])

    piece.on_command(cmd, now_ms=100, dst_empty=True)

    state.process_command.assert_not_called()
    assert piece._state == state
    assert piece._current_cmd is None


def test_is_command_possible_pawn_forward_one_step():
    state = make_mock_state()
    state._physics.board.algebraic_to_cell.return_value = (5, 4)
    state._physics.start_cell = (6, 4)
    state._moves.get_moves.return_value = [(5, 4)]

    piece = Piece("PW_1", state)
    cmd = Command(0, "PW_1", "move", [(6, 4), (5, 4)])

    assert piece.is_command_possible(cmd, dst_empty=True) is True


def test_is_command_possible_pawn_illegal_move():
    state = make_mock_state()
    state._physics.board.algebraic_to_cell.return_value = (4, 5)
    state._physics.start_cell = (6, 4)
    state._moves.get_moves.return_value = []

    piece = Piece("PW_1", state)
    cmd = Command(0, "PW_1", "move", [(6, 4), (4, 5)])

    assert piece.is_command_possible(cmd, dst_empty=True) is False


def test_update_triggers_auto_transition_when_finished():
    next_state = make_mock_state("idle")
    state = make_mock_state("move", transitions={"done": next_state})
    state._physics.finished = True
    state._physics.get_pos_in_cell.return_value = (4, 4)

    piece = Piece("PW_1", state)
    piece._current_cmd = Command(0, "PW_1", "move", [(4, 4), (4, 5)])

    piece.update(1000)

    assert piece._state == next_state
    state.update.assert_called_once_with(1000)


def test_reset_invokes_state_reset_with_last_command():
    state = make_mock_state()
    piece = Piece("PW_1", state)
    cmd = Command(0, "PW_1", "move", [(4, 4), (4, 5)])
    piece._current_cmd = cmd

    piece.reset(start_ms=500)

    state.reset.assert_called_once_with(cmd)


def test_clone_to_creates_new_piece_with_new_physics():
    original_state = make_mock_state()
    original_state._graphics.copy.return_value = MagicMock()
    original_state._physics.__class__.__name__ = "MovePhysics"
    original_state._physics.speed = 2.0

    factory = MagicMock()
    new_physics = MagicMock()
    factory.create.return_value = new_physics

    new_state = MagicMock()
    new_state.set_transition = MagicMock()

    piece = Piece("PW_1", original_state)
    cloned = piece.clone_to((2, 2), factory)

    factory.create.assert_called_once()
    assert isinstance(cloned, Piece)
    assert cloned.get_id() == "PW_1"
