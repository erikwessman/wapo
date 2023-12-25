from typing import Dict, List

from managers.base_manager import Manager
from classes.player import Player
from classes.item import Item


class PlayerManager(Manager):
    """"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self._players = self._read_data()

    def _read_data(self) -> Dict[str, Player]:
        raw_data = super()._read_data()
        return {key: Player.from_dict(item_data) for key, item_data in raw_data.items()}

    def save_data(self) -> None:
        data = {key: item.__dict__ for key, item in self._players.items()}
        super()._write_data(data)

    def register_player(self, player_id: int) -> Player:
        if player_id in self._players:
            raise ValueError(f"Player with ID {player_id} already exists.")

        player = Player(player_id)
        self._players[player_id] = player
        return player

    def get_players(self) -> List[Player]:
        return self._players.values()

    def get_player(self, player_id: int) -> Player:
        if not self.has_player(player_id):
            return self.register_player(player_id)
        return self._players[player_id]

    def has_player(self, player_id: int) -> bool:
        return player_id in self._players

    def handle_buy_item(self, player_id: int, item: Item):
        player = self.get_player(player_id)

        player.items[item.item_id] += 1
        player.tokens -= item.price

    def handle_remove_item(self, player_id: int, item: Item) -> bool:
        player = self.get_player(player_id)

        player.items[item.item_id] -= 1

        if player.items[item.item_id] <= 0:
            del player.items[item.item_id]

    def get_player_items(self, player_id: int) -> Dict[str, int]:
        player = self.get_player(player_id)
        return player.items

    def update_tokens(self, player_id: int, nr_tokens: int) -> None:
        player = self.get_player(player_id)
        player.tokens += nr_tokens

    def set_tokens(self, player_id: int, nr_tokens: int) -> None:
        player = self.get_player(player_id)
        player.tokens = nr_tokens

    def get_tokens(self, player_id: int) -> int:
        player = self.get_player(player_id)
        return player.tokens
