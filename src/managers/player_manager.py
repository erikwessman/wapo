from typing import List

from manager import Manager
from player import Player


class PlayerManager(Manager):
    """
    Manages player information persistently
    """

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def register_player(self, player_id: int) -> None:
        data = self._read_data()
        data[player_id] = Player(player_id)

        self._write_data(data)

    def get_players(self) -> List[Player]:
        data = self._read_data()
        return list(data.values())

    def get_player(self, player_id: int) -> Player:
        data = self._read_data()
        player_id_str = str(player_id)

        return data[player_id_str]

    def player_exists(self, player_id: int) -> bool:
        data = self._read_data()
        player_id_str = str(player_id)

        return player_id_str in data

    def add_item_to_player(self, player_id: int, item_id: int) -> bool:
        pass

    def remove_item_from_player(self) -> bool:
        pass

    def update_tokens(self, player_id: int, nr_tokens: int) -> None:
        data = self._read_data()

        player_id_str = str(player_id)
        player = data[player_id_str]
        player.tokens += nr_tokens

        self._write_data(data)

    def set_tokens(self, player_id: int, nr_tokens: int) -> None:
        data = self._read_data()

        player_id_str = str(player_id)
        player = data[player_id_str]
        player.tokens = nr_tokens

        self._write_data(data)

    def get_tokens(self, player_id: int) -> int:
        data = self._read_data()

        player_id_str = str(player_id)
        player = data[player_id_str]

        return player.tokens
