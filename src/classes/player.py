from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Player:
    """
    Represents a player/user in the Discord server
    """

    id: int
    inventory: Dict[str, int] = field(default_factory=dict)
    tokens: int = 0
