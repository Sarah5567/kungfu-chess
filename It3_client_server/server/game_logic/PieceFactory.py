import pathlib
from typing import Dict, Tuple
import json
from server.game_logic.Board import Board
from server.game_logic.Moves import Moves
from server.game_logic.PhysicsFactory import PhysicsFactory
from server.game_logic.Piece import Piece
from server.game_logic.State import State


class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root
        self._physics_factory = PhysicsFactory(board)
        self._templates: Dict[str, Piece] = {}
        self.counter = {}
    def _build_state_machine(self, piece_dir: pathlib.Path, cell: Tuple[int, int]) -> State:
        """Build a state machine for a piece from its directory."""
        states: Dict[str, State] = {}
        moves = Moves(piece_dir / "moves.txt", (self.board.H_cells, self.board.W_cells))
        states_root = piece_dir / "states"
        for state_dir in states_root.iterdir():
            if not state_dir.is_dir():
                continue
            state_name = state_dir.name.upper()
            cfg_path = state_dir / "config.json"
            with open(cfg_path, "r") as f:
                cfg = json.load(f)
            physics = self._physics_factory.create(
                state_name,
                cell,
                cfg["physics"]
            )
            states[state_name] = State(moves, physics)
        states['IDLE'].set_transition('MOVE', states['MOVE'])
        states['IDLE'].set_transition('JUMP', states['JUMP'])
        states['MOVE'].set_transition('LONG_REST', states['LONG_REST'])
        states['JUMP'].set_transition('SHORT_REST', states['SHORT_REST'])
        states['LONG_REST'].set_transition('IDLE', states['IDLE'])
        states['SHORT_REST'].set_transition('IDLE', states['IDLE'])
        return states['IDLE']

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
