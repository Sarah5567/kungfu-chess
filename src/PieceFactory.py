import pathlib
from typing import Dict, Tuple
import json
from Board import Board
from GraphicsFactory import GraphicsFactory
from Moves import Moves
from PhysicsFactory import PhysicsFactory
from Piece import Piece
from State import State
from enums.StatesNames import StatesNames


class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root
        self._physics_factory = PhysicsFactory(board)
        self._graphics_factory = GraphicsFactory(board)
        self._templates: Dict[str, Piece] = {}
        self.counter = {}
    def _build_state_machine(self, piece_dir: pathlib.Path, cell: Tuple[int, int]) -> State:
        """Build a state machine for a piece from its directory."""
        states: Dict[StatesNames, State] = {}
        moves = Moves(piece_dir / "moves.txt", (self.board.H_cells, self.board.W_cells))
        states_root = piece_dir / "states"
        for state_dir in states_root.iterdir():
            if not state_dir.is_dir():
                continue
            state_name = StatesNames(state_dir.name)
            cfg_path = state_dir / "config.json"
            with open(cfg_path, "r") as f:
                cfg = json.load(f)
            physics = self._physics_factory.create(
                state_name,
                cell,
                cfg["physics"]
            )
            graphics = self._graphics_factory.load(
                state_dir / "sprites",
                cfg["graphics"],
                (self.board.cell_H_pix, self.board.cell_W_pix)
            )
            states[state_name] = State(moves, graphics, physics)
        states[StatesNames.IDLE].set_transition(StatesNames.MOVE, states[StatesNames.MOVE])
        states[StatesNames.IDLE].set_transition(StatesNames.JUMP, states[StatesNames.JUMP])
        states[StatesNames.MOVE].set_transition(StatesNames.LONG_REST, states[StatesNames.LONG_REST])
        states[StatesNames.JUMP].set_transition(StatesNames.SHORT_REST, states[StatesNames.SHORT_REST])
        states[StatesNames.LONG_REST].set_transition(StatesNames.IDLE, states[StatesNames.IDLE])
        states[StatesNames.SHORT_REST].set_transition(StatesNames.IDLE, states[StatesNames.IDLE])
        return states[StatesNames.IDLE]

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        if p_type not in self._templates:
            piece_dir = self.pieces_root / p_type
            init_state = self._build_state_machine(piece_dir,cell)
        if p_type not in self.counter:
            self.counter[p_type] = 0
        self.counter[p_type] += 1
        unique_id = f"{p_type}_{self.counter[p_type]}"
        # Create and return the piece with the unique id.
        piece = Piece(piece_id=unique_id, init_state=init_state)
        return piece
