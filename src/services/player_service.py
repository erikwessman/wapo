from typing import List
from discord.ext.commands import CommandError

from db import DB
from schemas.player import Player
from schemas.item import Item
from schemas.holding import Holding
from schemas.avatar import Avatar
from helper import calculate_new_average_price


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

    def add_coins(self, player_id: int, amount: int):
        player = self.get_player(player_id)

        if amount < 0:
            raise ValueError("Cannot add negative coins")

        player.coins += amount
        self.db.update_player(player)

    def remove_coins(self, player_id: int, amount: int):
        player = self.get_player(player_id)

        if amount < 0:
            raise ValueError("Cannot remove negative coins")

        if player.coins < amount:
            raise PlayerError("Insufficient coins")

        player.coins -= amount
        self.db.update_player(player)

    def buy_item(self, player_id: int, item: Item, quantity: int = 1):
        player = self.get_player(player_id)

        if player.coins < item.price * quantity:
            raise PlayerError("Insufficient coins")

        if item.id in player.inventory:
            player.inventory[item.id] += quantity
        else:
            player.inventory[item.id] = quantity

        player.coins -= item.price * quantity
        self.db.update_player(player)

    def remove_item(self, player_id: int, item: Item, quantity: int = 1):
        player = self.get_player(player_id)

        if item.id not in player.inventory:
            raise PlayerError("Item not in inventory")

        player.inventory[item.id] -= quantity

        if player.inventory[item.id] <= 0:
            del player.inventory[item.id]

        self.db.update_player(player)

    def add_item(self, player_id: int, item: Item, quantity: int = 1):
        """Add an item to a player without deducting their coins"""
        player = self.get_player(player_id)

        if item.id in player.inventory:
            player.inventory[item.id] += quantity
        else:
            player.inventory[item.id] = quantity

        self.db.update_player(player)

    def add_modifier(self, player_id: int, modifier_name: str):
        player = self.get_player(player_id)
        player.modifiers.append(modifier_name)
        self.db.update_player(player)

    def use_modifier(self, player_id: int, modifier_name: str):
        player = self.get_player(player_id)

        if modifier_name not in player.modifiers:
            raise PlayerError("You don't have this modifier")

        player.modifiers.remove(modifier_name)
        self.db.update_player(player)

    def has_modifier(self, player_id: int, modifier_name: str):
        player = self.get_player(player_id)
        return modifier_name in player.modifiers

    def update_flex_level(self, player_id: int, flex_level: int):
        player = self.get_player(player_id)
        player.flex_level = flex_level
        self.db.update_player(player)

    def update_avatar(self, player_id: int, icon: str):
        player = self.get_player(player_id)

        if icon not in player.avatars:
            raise PlayerError("You don't have this avatar")

        player.active_avatar = icon
        self.db.update_player(player)

    def add_avatar(self, player_id: int, icon: str, rarity: str):
        player = self.get_player(player_id)

        if icon in player.avatars:
            player.avatars[icon].count += 1
        else:
            player.avatars[icon] = Avatar(icon=icon, rarity=rarity, count=1)

        self.db.update_player(player)

    def buy_stock(self, player_id: int, ticker: str, price: int, quantity: int = 1):
        player = self.get_player(player_id)

        if player.coins < price * quantity:
            raise PlayerError("Insufficient coins")

        if price <= 0:
            raise PlayerError("Can't buy a stock for 0")

        if ticker in player.holdings:
            # Calculate the new average price before updating the shares
            initial_shares = player.holdings[ticker].shares
            initial_price = player.holdings[ticker].average_price

            new_avg = calculate_new_average_price(
                initial_shares, initial_price, quantity, price
            )

            player.holdings[ticker].shares += quantity
            player.holdings[ticker].average_price = new_avg
        else:
            player.holdings[ticker] = Holding(
                ticker=ticker, shares=quantity, average_price=price
            )

        player.coins -= price * quantity
        self.db.update_player(player)

    def sell_stock(self, player_id: int, ticker: str, price: int, quantity: int = 1):
        player = self.get_player(player_id)

        if ticker not in player.holdings:
            raise PlayerError(f"You do not own any shares of ${ticker}")

        if price <= 0:
            raise PlayerError("Can't sell a stock for 0")

        if player.holdings[ticker].shares < quantity:
            raise PlayerError("Not enough shares")

        player.holdings[ticker].shares -= quantity

        if player.holdings[ticker].shares <= 0:
            del player.holdings[ticker]

        player.coins += price * quantity
        self.db.update_player(player)


class PlayerError(CommandError):
    """
    Exception raised when interacting with a player
    """
