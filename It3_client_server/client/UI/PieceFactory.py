import pathlib
from typing import Dict, Tuple
import json
from client.UI.Board import Board
from client.UI.GraphicsFactory import GraphicsFactory
# from client.UI.PhysicsFactory import PhysicsFactory
from client.UI.Piece import Piece
from client.UI.State import State


class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root
        # self._physics_factory = PhysicsFactory(board)
        self._graphics_factory = GraphicsFactory(board)
        self._templates: Dict[str, Piece] = {}
        self.counter = {}
    def _build_state_machine(self, piece_dir: pathlib.Path, cell: Tuple[int, int]) -> State:
        """Build a state machine for a piece from its directory."""
        states: Dict[str, State] = {}
        # moves = Moves(piece_dir / "moves.txt", (self.board.H_cells, self.board.W_cells))
        states_root = piece_dir / "states"
        for state_dir in states_root.iterdir():
            if not state_dir.is_dir():
                continue
            state_name = state_dir.name
            cfg_path = state_dir / "config.json"
            with open(cfg_path, "r") as f:
                cfg = json.load(f)
            graphics = self._graphics_factory.load(
                state_dir / "sprites",
                cfg["graphics"],
                (self.board.cell_H_pix, self.board.cell_W_pix)
            )
            states[state_name] = State(graphics)
        states['IDLE'].set_transition('MOVE', states['MOVE'])
        states['IDLE'].set_transition('JUMP', states['JUMP'])
        states['MOVE'].set_transition('LONG_REST', states['LONG_REST'])
        states['JUMP'].set_transition('SHORT_REST', states['SHORT_REST'])
        states['LONG_REST'].set_transition('IDLE', states['IDLE'])
        states['SHORT_REST'].set_transition('IDLE', states['IDLE'])
        return states['IDLE']

    def create_piece(self, piece_id: str, cell: Tuple[int, int]) -> Piece:
        p_type : str = piece_id[:2]
        if p_type not in self._templates:
            piece_dir = self.pieces_root / p_type
            init_state = self._build_state_machine(piece_dir,cell)
        # Create and return the piece with the unique id.
        piece = Piece(piece_id=piece_id, init_state=init_state)
        return piece
