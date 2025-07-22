# Moves.py  – drop-in replacement
import pathlib
from typing import List, Tuple
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

