import json
from typing import List, Dict
from discord.ext.commands import CommandError

from schemas.item import Item


class Store:
    """
    Represents a store that provides information on available items
    """

    def __init__(self, file_path: str):
        self._items = self._load_items(file_path)

    def _load_items(self, file_path: str) -> Dict[str, Item]:
        try:
            with open(file_path, "r") as file:
                raw_data = json.load(file)
                return {key: Item(**item_data) for key, item_data in raw_data.items()}
        except FileNotFoundError:
            raise StoreError(f"The file '{file_path}' was not found.")
        except json.JSONDecodeError:
            raise StoreError(f"Could not decode the contents of '{file_path}'")

    def get_item(self, item_id: str) -> Item:
        """Get an item from the store"""
        if item_id not in self._items:
            raise StoreError(f"Item with id {item_id} does not exist")

        return self._items.get(item_id)

    def get_items(self) -> List[Item]:
        """Get all the items the store"""
        return list(self._items.values()).copy()


class StoreError(CommandError):
    """Exception raised when interacting with the store"""
