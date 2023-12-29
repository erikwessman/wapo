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

    def update_coins(self, player_id: int, amount: int):
        player = self.get_player(player_id)
        player.coins += amount
        self.db.update_player(player)

    def buy_item(self, player_id: int, item: Item, quantity: int = 1):
        player = self.get_player(player_id)
        if item.id in player.inventory:
            player.inventory[item.id] += quantity
        else:
            player.inventory[item.id] = quantity
        player.coins -= item.price * quantity
        self.db.update_player(player)

    def remove_item(self, player_id: int, item: Item, quantity: int = 1):
        player = self.get_player(player_id)
        player.inventory[item.id] -= quantity

        if player.inventory[item.id] <= 0:
            del player.inventory[item.id]

        self.db.update_player(player)

    def add_modifier(self, player_id: int, modifier_name: str):
        player = self.get_player(player_id)
        player.modifiers.append(modifier_name)
        self.db.update_player(player)

    def use_modifier(self, player_id: int, modifier_name: str):
        player = self.get_player(player_id)
        player.modifiers.remove(modifier_name)
        self.db.update_player(player)

    def update_flex_level(self, player_id: int, flex_level: int):
        player = self.get_player(player_id)
        player.flex_level = flex_level
        self.db.update_player(player)
