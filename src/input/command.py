from dataclasses import dataclass
from typing import List
from src.enums.states_names import StatesNames


@dataclass
class Command:
    timestamp: int          # ms since game start
    piece_id: str
    type: StatesNames               # "Move" | "Jump" | …
    params: List          # payload (e.g. ["e2", "e4"])