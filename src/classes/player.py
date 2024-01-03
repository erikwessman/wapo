from typing import Dict, List
from dataclasses import dataclass, field

from classes.holding import Holding


@dataclass
class Player:
    """
    Represents a player/user in the Discord server
    """

    id: int
    inventory: Dict[str, int] = field(default_factory=dict)
    coins: float = 0
    modifiers: List[str] = field(default_factory=list)
    flex_level: int = 0
    horse_icon: str = None
    holdings: Dict[str, Holding] = field(default_factory=dict)
