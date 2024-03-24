from datetime import datetime
from typing import Dict
from mongoengine import Document, EmbeddedDocumentField, IntField, StringField, MapField
from schemas.player_item import PlayerItem
from schemas.player_modifier import PlayerModifier
from schemas.player_avatar import PlayerAvatar
from schemas.player_holding import PlayerHolding

from helper import calculate_new_average_price


class Player(Document):
    """
    Represents a player/user in the Discord server
    """

    id = IntField(primary_key=True)
    coins = IntField(default=10)  # Players start with 10 coins
    active_avatar = StringField(default="")
    inventory = MapField(EmbeddedDocumentField(PlayerItem), default=lambda: {})
    modifiers = MapField(EmbeddedDocumentField(PlayerModifier), default=lambda: {})
    avatars = MapField(EmbeddedDocumentField(PlayerAvatar), default=lambda: {})
    holdings = MapField(EmbeddedDocumentField(PlayerHolding), default=lambda: {})

    meta = {"collection": "players"}

    def get_active_avatar(self) -> str:
        return self.active_avatar

    def set_active_avatar(self, avatar: str):
        self.active_avatar = avatar
        self.save()

    def get_coins(self) -> int:
        return self.coins

    def add_coins(self, amount: int):
        if amount < 1:
            raise ValueError("Must add at least 1 coin")

        self.coins += amount
        self.save()

    def remove_coins(self, amount: int):
        if amount < 1:
            raise ValueError("Must remove at least 1 coin")

        if self.coins < amount:
            raise ValueError("Not enough coins")

        self.coins -= amount
        self.save()

    def set_coins(self, amount: int):
        self.coins = amount
        self.save()

    def get_item(self, itemid: str) -> PlayerItem:
        if itemid not in self.inventory:
            raise ValueError("Player does not have this item")

        return self.inventory[itemid]

    def get_items(self) -> Dict[str, PlayerItem]:
        return self.inventory

    def has_item(self, itemid: str) -> bool:
        return itemid in self.inventory

    def add_item(self, itemid: str, amount: int = 1):
        if itemid in self.inventory:
            self.inventory[itemid].amount += amount
        else:
            self.inventory[itemid] = PlayerItem(id=itemid, amount=amount)
        self.save()

    def remove_item(self, itemid: str, amount: int = 1):
        if itemid not in self.inventory:
            raise ValueError("Player does not have this item")

        player_item = self.inventory[itemid]

        if player_item.amount < amount:
            raise ValueError("Player does not have enough items to remove")

        player_item.amount -= amount

        if player_item.amount < 1:
            del self.inventory[itemid]

        self.save()

    def get_modifier(self, modifier_id: str) -> PlayerModifier:
        if modifier_id not in self.modifiers:
            raise ValueError("Player does not have this modifier")

        return self.modifiers[modifier_id]

    def get_modifiers(self) -> Dict[str, PlayerModifier]:
        return self.modifiers

    def has_modifier(self, modifier_id: str) -> bool:
        return modifier_id in self.modifiers

    def add_modifier(self, modifier_id: str, stacks: int = 1):
        if modifier_id in self.modifiers:
            self.modifiers[modifier_id].stacks += stacks
            self.modifiers[modifier_id].last_used = datetime.utcnow()
        else:
            self.modifiers[modifier_id] = PlayerModifier(
                id=modifier_id, stacks=stacks, last_used=datetime.utcnow()
            )
        self.save()

    def remove_modifier(self, modifierid: str):
        if modifierid in self.modifiers:
            del self.modifiers[modifierid]
            self.save()

    def get_avatar(self, avatar: str) -> PlayerAvatar:
        if avatar not in self.avatars:
            raise ValueError("Player does not have this avatar")

        return self.avatars[avatar]

    def get_avatars(self) -> Dict[str, PlayerAvatar]:
        return self.avatars

    def has_avatar(self, avatar: str) -> bool:
        return avatar in self.avatars

    def add_avatar(self, avatar: str, rarity: str, count: int = 1):
        if avatar in self.avatars:
            self.avatars[avatar].count += count
        else:
            self.avatars[avatar] = PlayerAvatar(icon=avatar, rarity=rarity, count=count)
        self.save()

    def remove_avatar(self, avatarid: str):
        if avatarid in self.avatars:
            del self.avatars[avatarid]
            self.save()

    def get_holding(self, ticker) -> PlayerHolding:
        if ticker not in self.holdings:
            raise ValueError("Player does not have this holding")

        return self.holdings[ticker]

    def get_holdings(self) -> Dict[str, PlayerHolding]:
        return self.holdings

    def has_holding(self, ticker: str) -> bool:
        return ticker in self.holdings

    def add_holding(self, ticker: str, shares: int, price: int):
        if ticker in self.holdings:
            # Calculate the new average price before updating the shares
            initial_shares = self.holdings[ticker].shares
            initial_price = self.holdings[ticker].average_price

            new_avg = calculate_new_average_price(
                initial_shares, initial_price, shares, price
            )

            self.holdings[ticker].shares += shares
            self.holdings[ticker].average_price = new_avg
        else:
            self.holdings[ticker] = PlayerHolding(
                ticker=ticker, shares=shares, average_price=price
            )
        self.save()

    def remove_holding(self, ticker: str, shares: int = 1):
        if ticker not in self.holdings:
            raise ValueError("Player does not have this holding")

        player_holding = self.holdings[ticker]

        if player_holding.shares < shares:
            raise ValueError("Player does not have enough holdings to remove")

        player_holding.shares -= shares

        if player_holding.shares < 1:
            del self.holdings[ticker]

        self.save()
