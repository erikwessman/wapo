from typing import List

from db import DB
from classes.player import Player
from classes.item import Item


class PlayerService:
    """
    Service layer for interacting with and getting players from the database
    """

    def __init__(self, db: DB):
        self.db = db

    def add_player(self, player_id: int) -> Player:
        if self.db.has_player(player_id):
            raise ValueError("Player already exists")

        player = Player(id=player_id)
        self.db.add_player(player)
        return player

    def get_player(self, player_id: int) -> Player:
        if not self.db.has_player(player_id):
            return self.add_player(player_id)

        return self.db.get_player(player_id)

    def get_players(self) -> List[Player]:
        return self.db.get_players()

    def update_tokens(self, player_id: int, amount: int):
        player = self.get_player(player_id)
        player.tokens += amount
        self.db.update_player(player)

    def buy_item(self, player_id: int, item: Item, quantity: int = 1):
        player = self.get_player(player_id)
        item_id_str = str(item.id)
        if item_id_str in player.inventory:
            player.inventory[item_id_str] += quantity
        else:
            player.inventory[item_id_str] = quantity
        player.tokens -= item.price * quantity
        self.db.update_player(player)

    def remove_item(self, player_id: int, item: Item, quantity: int = 1):
        player = self.get_player(player_id)
        player.inventory[item._id] -= quantity

        if player.inventory[item._id] <= 0:
            del player.inventory[item._id]

        self.db.update_player(player)
