from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Player:
    """
    Represents a player/user in the Discord server
    """

    id: int
    inventory: Dict[str, int] = field(default_factory=dict)
    coins: int = 0
    modifiers: List[str] = field(default_factory=list)

    def has_modifier(self, modifier_name) -> bool:
        return modifier_name in self.modifiers
