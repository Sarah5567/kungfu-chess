from dataclasses import dataclass
from typing import List
from server.game_logic.enums.StatesNames import StatesNames


@dataclass
class Command:
    timestamp: int          # ms since game start
    piece_id: str
    type: StatesNames               # "Move" | "Jump" | …
    params: List          # payload (e.g. ["e2", "e4"])