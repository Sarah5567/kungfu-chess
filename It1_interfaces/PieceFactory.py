import pathlib
from typing import Dict, Tuple
import json
from Board import Board
from GraphicsFactory import GraphicsFactory
from Moves import Moves
from PhysicsFactory import PhysicsFactory
from Piece import Piece
from State import State

class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root
        self._physics_factory = PhysicsFactory(board)
        self._graphics_factory = GraphicsFactory(board)
        self._templates: Dict[str, Piece] = {}

    def _build_state_machine(self, piece_dir: pathlib.Path) -> State:
        """Build a state machine for a piece from its directory."""
        states: Dict[str, State] = {}

        moves = Moves(piece_dir / "moves.txt", (self.board.H_cells, self.board.W_cells))
        states_root = piece_dir / "states"

        for state_dir in states_root.iterdir():
            if not state_dir.is_dir():
                continue
            state_name = state_dir.name
            cfg_path = state_dir / "config.json"
            with open(cfg_path, "r") as f:
                cfg = json.load(f)

            dummy_start_cell = (1, 0)

            physics = self._physics_factory.create(
                state_name,
                dummy_start_cell,
                cfg["physics"]
            )

            graphics = self._graphics_factory.load(
                state_dir / "sprites",
                cfg["graphics"],
                (self.board.cell_H_pix, self.board.cell_W_pix)
            )

            states[state_name] = State(moves, graphics, physics)

        states["idle"].set_transition("move", states["move"])
        states["idle"].set_transition("jump", states["jump"])

        states["move"].set_transition("long_rest", states["long_rest"])
        states["jump"].set_transition("short_rest", states["short_rest"])

        states["long_rest"].set_transition("idle", states["idle"])
        states["short_rest"].set_transition("idle", states["idle"])

        return states["idle"]

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        if p_type not in self._templates:
            piece_dir = self.pieces_root / p_type
            template_state = self._build_state_machine(piece_dir)
            self._templates[p_type] = template_state

        # יצירת עותק עמוק של כל המצבים והטרנזיציות
        init_state = self._deep_copy_state_machine(self._templates[p_type], cell)
        return Piece(p_type, init_state)

    def _deep_copy_state_machine(self, template_state: State, cell: Tuple[int, int]) -> State:
        state_mapping = {}
        
        def copy_state(state: State) -> State:
            if state in state_mapping:
                return state_mapping[state]
                
            raw_state_name = state._physics.__class__.__name__.replace("Physics", "").lower().strip()
            # אם הערך שחושב לא תואם, נניח שהמצב הוא idle (כך בהתחלה הכל במצב idle)
            state_name = raw_state_name if raw_state_name in ["idle", "move", "jump", "short_rest", "long_rest"] else "idle"
            
            new_physics = self._physics_factory.create(state_name, cell, {})
            new_state = State(state._moves, state._graphics, new_physics)
            
            state_mapping[state] = new_state
            
            # העתקת הטרנזיציות תוך כדי קריאה רקורסיבית, כך שהמפה לא משתנה תוך כדי איטרציה
            for event, target in state.transitions.items():
                new_target = copy_state(target)
                new_state.set_transition(event, new_target)
            return new_state

        return copy_state(template_state)
