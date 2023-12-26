from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Player:
    id: int
    inventory: Dict[str, int] = field(default_factory=dict)
    tokens: int = 0
