from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass
class Command:
    timestamp: int          # ms since game start
    piece_id: str
    type: str               # "Move" | "Jump" | …
    params: List            # payload (e.g. ["e2", "e4"]) 