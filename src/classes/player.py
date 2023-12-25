from collections import defaultdict
from typing import Dict


class Player:
    """"""

    def __init__(self, player_id: int, items: dict = {}, tokens: int = 0):
        self._player_id = player_id
        self._items = defaultdict(int, items)
        self._tokens = tokens

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def items(self) -> Dict[str, int]:
        return self._items

    @property
    def tokens(self) -> int:
        return self._tokens

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
