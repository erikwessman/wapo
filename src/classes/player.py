from collections import defaultdict
from typing import Dict


class Player:
    """"""

    def __init__(self,
                 player_id: int,
                 inventory: dict = {},
                 tokens: int = 0):
        self._player_id = player_id
        self._inventory = defaultdict(int, inventory)
        self._tokens = tokens

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def inventory(self) -> Dict[str, int]:
        return self._inventory

    @property
    def tokens(self) -> int:
        return self._tokens

    def __str__(self):
        return (
            f"Player ID: {self._player_id}, "
            f"Inventory: {self._inventory} "
            f"Tokens: {self._tokens}"
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
