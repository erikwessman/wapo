from typing import List
from datetime import datetime
from discord.ext.commands import BadArgument

from db import DB
from schemas.player import Player
from schemas.modifier import Modifier
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
            raise BadArgument("Player already exists")

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
            raise BadArgument("Cannot add negative coins")

        player.coins += amount
        self.db.update_player(player)

    def remove_coins(self, player: Player, amount: int):
        if amount < 0:
            raise BadArgument("Cannot remove negative coins")

        if player.coins < amount:
            raise BadArgument("Insufficient coins")

        player.coins -= amount
        self.db.update_player(player)

    def buy_item(self, player: Player, item: Item, quantity: int = 1):
        if quantity < 1:
            raise BadArgument("Must buy at least 1 item")

        if player.coins < item.price * quantity:
            raise BadArgument("Insufficient coins")

        if item.name in player.inventory:
            player.inventory[item.name] += quantity
        else:
            player.inventory[item.name] = quantity

        player.coins -= item.price * quantity
        self.db.update_player(player)

    def remove_item(self, player: Player, item: Item, quantity: int = 1):
        if quantity < 1:
            raise BadArgument("Canont remove negative amount of items")

        if item.name not in player.inventory:
            raise BadArgument("Item not in player inventory")

        player.inventory[item.name] -= quantity

        if player.inventory[item.name] <= 0:
            del player.inventory[item.name]

        self.db.update_player(player)

    def add_item(self, player: Player, item: Item, quantity: int = 1):
        """Add an item to a player without deducting their coins"""
        if item.name in player.inventory:
            player.inventory[item.name] += quantity
        else:
            player.inventory[item.name] = quantity

        self.db.update_player(player)

    def add_modifier(self, player: Player, modifier_name: str):
        if modifier_name in player.modifiers:
            player.modifiers[modifier_name].amount += 1
        else:
            player.modifiers[modifier_name] = Modifier(name=modifier_name, amount=1)

        player.modifiers[modifier_name].last_used = datetime.utcnow()
        self.db.update_player(player)

    def remove_modifier(self, player: Player, modifier_name: str):
        if modifier_name not in player.modifiers or player.modifiers[modifier_name].count < 1:
            raise BadArgument("You don't have this modifier")

        player.modifiers[modifier_name].amount -= 1

        if player.modifiers[modifier_name].amount < 1:
            del player.modifiers[modifier_name]

        self.db.update_player(player)

    def has_modifier(self, player: Player, modifier_name: str):
        return modifier_name in player.modifiers and player.modifiers[modifier_name].count > 0

    def update_avatar(self, player: Player, icon: str):
        if icon not in player.avatars:
            raise BadArgument("You don't have this avatar")

        player.active_avatar = icon
        self.db.update_player(player)

    def add_avatar(self, player: Player, icon: str, rarity: str):
        if icon in player.avatars:
            player.avatars[icon].count += 1
        else:
            player.avatars[icon] = Avatar(icon=icon, rarity=rarity, count=1)

        self.db.update_player(player)

    def buy_stock(self, player: Player, ticker: str, price: int, quantity: int = 1):
        if quantity < 1:
            raise BadArgument("Must buy at least one share")

        if player.coins < price * quantity:
            raise BadArgument("Insufficient coins")

        if price <= 0:
            raise BadArgument("Can't buy a stock for 0 coins")

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
        if quantity < 1:
            raise BadArgument("Must sell at least one share")

        if ticker not in player.holdings:
            raise BadArgument(f"You do not own any shares of ${ticker}")

        if price <= 0:
            raise BadArgument("Can't sell a stock for 0 coins")

        if player.holdings[ticker].shares < quantity:
            raise BadArgument("Not enough shares")

        player.holdings[ticker].shares -= quantity

        if player.holdings[ticker].shares <= 0:
            del player.holdings[ticker]

        player.coins += price * quantity
        self.db.update_player(player)
