import pathlib
from typing import List, Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from Piece import Piece


class Moves:
    def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
        """Initialize moves with rules from text file and board dimensions."""
        self.dims = dims  # Dimensions of the board (rows, cols)
        self.rules = self._load_rules(txt_path)  # Load movement rules from file

    def _load_rules(self, txt_path: pathlib.Path) -> List[Tuple[int, int]]:
        """Load movement rules from a text file."""
        rules = []
        try:
            with txt_path.open('r') as file:
                for line in file:
                    # Parse each line as a tuple of integers (e.g., "1,2" -> (1, 2))
                    parts = line.strip().split(',')
                    if len(parts) != 2:
                        raise ValueError(f"Invalid format on line: {line}")
                    rules.append((int(parts[0]), int(parts[1])))
        except Exception as e:
            raise ValueError(f"Error loading rules from {txt_path}: {e}")
        return rules

    def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Get all possible moves from a given position."""
        possible_moves = []
        for dr, dc in self.rules:
            new_r, new_c = r + dr, c + dc
            # Check if the new position is within board boundaries
            if 0 <= new_r < self.dims[0] and 0 <= new_c < self.dims[1]:
                possible_moves.append((new_r, new_c))
        return possible_moves

    def is_move_legal(self, src: Tuple[int, int], dst: Tuple[int, int], pos_to_piece: Dict[Tuple[int, int], list], moving_piece: "Piece") -> bool:
        """Check if a move is legal. All checks are here."""
        # האם יש כלי בתא המקור
        if src not in pos_to_piece or not any(p.get_id() == moving_piece.get_id() for p in pos_to_piece[src]):
            print("Move blocked: No such piece in source cell.")
            return False

        # האם הכלי שייך לשחקן הנכון
        if moving_piece.get_id()[1] not in ['B', 'W']:
            print("Move blocked: Unknown player.")
            return False

        # האם הצעד חוקי לפי הכללים
        legal_moves = self.get_moves(*src)
        if dst not in legal_moves:
            print("Move blocked: Destination is not a legal move.")
            return False

        # האם תא היעד פנוי או אויב
        if dst in pos_to_piece:
            for target_piece in pos_to_piece[dst]:
                if target_piece.get_id()[1] == moving_piece.get_id()[1]:
                    print("Move blocked: Destination occupied by friendly piece.")
                    return False

        # האם הנתיב פנוי (אם רלוונטי)
        dx = dst[1] - src[1]
        dy = dst[0] - src[0]
        step_x = dx // abs(dx) if dx != 0 else 0
        step_y = dy // abs(dy) if dy != 0 else 0

        if (step_x != 0 or step_y != 0) and (abs(dx) == abs(dy) or dx == 0 or dy == 0):
            cur_cell = (src[0] + step_y, src[1] + step_x)
            while cur_cell != dst:
                if cur_cell in pos_to_piece and pos_to_piece[cur_cell]:
                    print("Move blocked: Path is obstructed.")
                    return False
                cur_cell = (cur_cell[0] + step_y, cur_cell[1] + step_x)

        return True
