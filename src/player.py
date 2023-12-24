from typing import List


class Player:
    def __init__(self, player_id: int):
        self._player_id = str(player_id)
        self._inventory = []
        self._tokens = 0

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def inventory(self) -> List[int]:
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
