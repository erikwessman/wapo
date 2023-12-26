from collections import defaultdict
from typing import Dict


class Player:
    """"""

    def __init__(self, id: int, initial_inventory: dict = {}, initial_tokens: int = 0):
        self._id = id
        self.inventory = defaultdict(int, initial_inventory)
        self._tokens = initial_tokens

    @property
    def id(self) -> int:
        return self._id

    @property
    def inventory(self) -> Dict[str, int]:
        return self.inventory

    @property
    def tokens(self) -> int:
        return self._tokens

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
