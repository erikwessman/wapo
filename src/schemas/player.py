from mongoengine import Document, EmbeddedDocumentField, IntField, StringField, MapField
from schemas.player_item import PlayerItem
from schemas.player_modifier import PlayerModifier
from schemas.player_avatar import PlayerAvatar
from schemas.player_holding import PlayerHolding

from typing import Dict


class Player(Document):
    """
    Represents a player/user in the Discord server
    """

    _id = IntField(primary_key=True)
    _coins = IntField(default=10)  # Players start with 10 coins
    _active_avatar = StringField(default="")
    _inventory = MapField(EmbeddedDocumentField(PlayerItem), default=lambda: {})
    _modifiers = MapField(EmbeddedDocumentField(PlayerModifier), default=lambda: {})
    _avatars = MapField(EmbeddedDocumentField(PlayerAvatar), default=lambda: {})
    _holdings = MapField(EmbeddedDocumentField(PlayerHolding), default=lambda: {})

    meta = {"collection": "players"}

    def get_active_avatar(self) -> str:
        return self._active_avatar

    def set_active_avatar(self, avatar: str):
        self._active_avatar = avatar

    def get_coins(self) -> int:
        return self._coins

    def add_coins(self, amount: int):
        if amount < 1:
            raise ValueError("Must add at least 1 coin")

        self._coins += amount
        self._save()

    def remove_coins(self, amount: int):
        if amount < 1:
            raise ValueError("Must remove at least 1 coin")

        if self._coins < amount:
            raise ValueError("Not enough coins")

        self._coins -= amount
        self._save()

    def set_coins(self, amount: int):
        self._coins = amount
        self.save()

    def get_item(self, item_id: str) -> PlayerItem:
        if item_id not in self._inventory:
            raise ValueError("Player does not have this item")

        return self._inventory[item_id]

    def get_items(self) -> Dict[str, PlayerItem]:
        return self._inventory

    def has_item(self, item_id: str) -> bool:
        return item_id in self._inventory

    def add_item(self, item_id: str, amount: int = 1):
        if item_id in self._inventory:
            self._inventory[item_id].amount += amount
        else:
            self._inventory[item_id] = PlayerItem(id=item_id, amount=amount)
        self.save()

    def remove_item(self, item_id: str, amount: int = 1):
        if item_id not in self._inventory:
            raise ValueError("Player does not have this item")

        player_item = self._inventory[item_id]

        if player_item.amount < amount:
            raise ValueError("Player does not have enough items to remove")

        player_item.amount -= amount

        if player_item.amount < 1:
            del self._inventory[item_id]

        self.save()

    def get_modifier(self, modifier_id: str) -> PlayerModifier:
        if modifier_id not in self._modifiers:
            raise ValueError("Player does not have this modifier")

        return self._modifiers[modifier_id]

    def get_modifiers(self) -> Dict[str, PlayerModifier]:
        return self._modifiers

    def has_modifier(self, modifier_id: str) -> bool:
        return modifier_id in self._modifiers

    def add_modifier(self, modifier_id: str, stacks: int = 1):
        if modifier_id in self._modifiers:
            self._modifiers[modifier_id].stacks += stacks
        else:
            self._modifiers[modifier_id] = PlayerModifier(id=modifier_id, stacks=stacks)
        self.save()

    def remove_modifier(self, modifier_id: str):
        if modifier_id in self._modifiers:
            del self._modifiers[modifier_id]
            self.save()

    def get_avatar(self, avatar: str) -> PlayerAvatar:
        if avatar not in self._avatars:
            raise ValueError("Player does not have this avatar")

        return self._avatars[avatar]

    def get_avatars(self) -> Dict[str, PlayerAvatar]:
        return self._avatars

    def has_avatar(self, avatar: str) -> bool:
        return avatar in self._avatars

    def add_avatar(self, avatar: str, rarity: str, count: int = 1):
        if avatar in self._avatars:
            self._avatars[avatar].count += count
        else:
            self._avatars[avatar] = PlayerAvatar(icon=avatar, rarity=rarity, count=count)
        self.save()

    def remove_avatar(self, avatar_id: str):
        if avatar_id in self._avatars:
            del self._avatars[avatar_id]
            self.save()

    def get_holding(self, ticker) -> PlayerHolding:
        if ticker not in self._holdings:
            raise ValueError("Player does not have this holding")

        return self._holdings[ticker]

    def get_holdings(self) -> Dict[str, PlayerHolding]:
        return self._holdings

    def has_holding(self, ticker: str) -> bool:
        return ticker in self._holdings

    def add_holding(self, ticker: str, shares: int, average_price: int):
        if ticker in self._holdings:
            self._holdings[ticker].shares += shares
            self._holdings[ticker].average_price += average_price
        else:
            self._holdings[ticker] = PlayerHolding(ticker=ticker, shares=shares, average_price=average_price)
        self.save()

    def remove_holding(self, ticker: str, shares: int = 1):
        if ticker not in self._holdings:
            raise ValueError("Player does not have this holding")

        player_holding = self._holdings[ticker]

        if player_holding.shares < shares:
            raise ValueError("Player does not have enough holdings to remove")

        player_holding.shares -= shares

        if player_holding.shares < 1:
            del self._holdings[ticker]

        self.save()
