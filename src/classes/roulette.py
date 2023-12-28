from dataclasses import dataclass
from typing import Dict


@dataclass
class Roulette:
    """
    Represents a game of roulette
    """

    id: str
    date: str
    players: Dict[int, int]
    winner: int
