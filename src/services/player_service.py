from typing import List

from db import DB
from classes.player import Player
from classes.item import Item


class PlayerService:
    def __init__(self, db: DB):
        self.db = db

    def add_player(self, player_id: int) -> Player:
        if self.db.has_player(player_id):
            raise ValueError("Player already exists")

        player = Player(player_id)
        self.db.add_player(player)
        return player

    def get_player(self, player_id: int) -> Player:
        if not self.db.has_player(player_id):
            return self.add_player(player_id)

        return self.db.get_player(player_id)

    def get_players(self) -> List[Player]:
        return self.db.get_players()

    def handle_player_update_tokens(self, player_id: int, amount: int):
        player = self.get_player(player_id)
        player.tokens += amount
        self.db.update_player(player)

    def handle_player_buy_item(self, player_id: int, item: Item, quantity: int = 1):
        player = self.get_player(player_id)
        player.items[item.item_id] += quantity
        self.db.update_player(player)

    def handle_player_remove_item(self, player_id: int, item: Item, quantity: int = 1):
        player = self.get_player(player_id)
        player.items[item.item_id] -= quantity

        if player.items[item.item_id] <= 0:
            del player.items[item.item_id]

        self.db.update_player(player)
