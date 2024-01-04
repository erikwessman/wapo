from typing import List
from discord.ext.commands import CommandError

from db import DB
from schemas.player import Player
from schemas.item import Item
from schemas.holding import Holding
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

    def add_coins(self, player: Player, amount: int):
        if amount < 0:
            raise ValueError("Cannot add negative coins")

        player.coins += amount
        self.db.update_player(player)

    def remove_coins(self, player: Player, amount: int):
        if amount < 0:
            raise ValueError("Cannot remove negative coins")

        if player.coins < amount:
            raise PlayerError("Insufficient coins")

        player.coins -= amount
        self.db.update_player(player)

    def buy_item(self, player: Player, item: Item, quantity: int = 1):
        if player.coins < item.price * quantity:
            raise PlayerError("Insufficient coins")

        if item.id in player.inventory:
            player.inventory[item.id] += quantity
        else:
            player.inventory[item.id] = quantity

        player.coins -= item.price * quantity
        self.db.update_player(player)

    def remove_item(self, player: Player, item: Item, quantity: int = 1):
        if item.id not in player.inventory:
            raise PlayerError("Item not in inventory")

        player.inventory[item.id] -= quantity

        if player.inventory[item.id] <= 0:
            del player.inventory[item.id]

        self.db.update_player(player)

    def add_modifier(self, player: Player, modifier_name: str):
        player.modifiers.append(modifier_name)
        self.db.update_player(player)

    def use_modifier(self, player: Player, modifier_name: str):
        player.modifiers.remove(modifier_name)
        self.db.update_player(player)

    def update_flex_level(self, player: Player, flex_level: int):
        player.flex_level = flex_level
        self.db.update_player(player)

    def update_horse_icon(self, player: Player, new_icon: str):
        player.horse_icon = new_icon
        self.db.update_player(player)

    def buy_stock(self, player: Player, ticker: str, price: int, quantity: int = 1):
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

    def sell_stock(self, player: Player, ticker: str, price: int, quantity: int = 1):
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
