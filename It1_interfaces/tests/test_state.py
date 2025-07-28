import pytest
from unittest.mock import MagicMock
from State import State
from Command import Command


def make_mock_state(name="mock", physics=None, graphics=None, moves=None):
    physics = physics or MagicMock()
    graphics = graphics or MagicMock()
    state = State(moves=moves, graphics=graphics, physics=physics)
    state.name = name
    return state




def test_state_reset_calls_physics_and_graphics():
    physics = MagicMock()
    graphics = MagicMock()
    state = State(moves=None, graphics=graphics, physics=physics)
    cmd = Command(0, "P", "idle", [(1, 1)])

    state.reset(cmd)

    physics.reset.assert_called_once_with(cmd)
    graphics.reset.assert_called_once_with(cmd)
    assert state.get_command() == cmd


def test_state_update_delegates_to_components():
    physics = MagicMock()
    graphics = MagicMock()
    state = State(moves=None, graphics=graphics, physics=physics)

    state.update(1234)

    physics.update.assert_called_once_with(1234)
    graphics.update.assert_called_once_with(1234)


def test_state_process_command_transitions_correctly():
    src_state = make_mock_state("idle")
    dst_state = make_mock_state("move")
    cmd = Command(0, "P", "move", [(0, 0), (1, 1)])

    src_state.set_transition("move", dst_state)
    result_state = src_state.process_command(cmd)

    assert result_state is dst_state


def test_state_command_possibility():
    state = make_mock_state()
    state.set_transition("move", make_mock_state("move"))
    state.set_transition("jump", make_mock_state("jump"))

    assert state.is_command_possible(Command(0, "P", "move", []))
    assert state.is_command_possible(Command(0, "P", "jump", []))
    assert not state.is_command_possible(Command(0, "P", "invalid", []))


def test_state_can_transition_based_on_physics_update():
    physics = MagicMock()
    state = State(moves=None, graphics=MagicMock(), physics=physics)

    physics.update.return_value = None
    assert not state.can_transition(1000)

    physics.update.return_value = Command(0, "P", "done", [])
    assert state.can_transition(1000)
