from dataclasses import dataclass
from typing import List


@dataclass
class Command:
    timestamp: int          # ms since game start
    piece_id: str
    type: str               # "Move" | "Jump" | …
    params: List          # payload (e.g. ["e2", "e4"])