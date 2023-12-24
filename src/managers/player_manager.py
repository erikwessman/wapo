from typing import Dict, List

from base_manager import Manager
from classes.player import Player
from classes.item import Item


class PlayerManager(Manager):
    """
    Manages player information persistently
    """

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def _read_data(self) -> Dict[str, Player]:
        raw_data = super()._read_data()
        return {key: Player.from_dict(item_data) for key, item_data in raw_data.items()}

    def _write_data(self, data) -> None:
        data = {key: item.__dict__ for key, item in data.items()}
        super()._write_data(data)

    def register_player(self, player_id: int) -> None:
        data = self._read_data()
        data[player_id] = Player(player_id)
        self._write_data(data)

    def get_players(self) -> List[Player]:
        data = self._read_data()
        return list(data.values())

    def get_player(self, player_id: int) -> Player:
        data = self._read_data()
        return data[player_id]

    def has_player(self, player_id: int) -> bool:
        data = self._read_data()
        return player_id in data

    def add_item_to_player(self, player_id: int, item: Item):
        data = self._read_data()
        player = data[player_id]

        player.items[item.item_id] += 1
        player.tokens -= item.price

        self._write_data(data)

    def remove_item_from_player(self, player_id: int, item: Item) -> bool:
        data = self._read_data()
        player = data[player_id]

        player.items[item.item_id] -= 1

        if player.items[item.item_id] <= 0:
            del player.items[item.item_id]

        self._write_data(data)

    def update_tokens(self, player_id: int, nr_tokens: int) -> None:
        data = self._read_data()
        player = data[player_id]
        player.tokens += nr_tokens

        self._write_data(data)

    def set_tokens(self, player_id: int, nr_tokens: int) -> None:
        data = self._read_data()
        player = data[player_id]
        player.tokens = nr_tokens

        self._write_data(data)

    def get_tokens(self, player_id: int) -> int:
        data = self._read_data()
        player = data[player_id]

        return player.tokens
