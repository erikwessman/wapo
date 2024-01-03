import json
from typing import List, Dict

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
            print(f"Error: The file '{file_path}' was not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode the contents of '{file_path}'.")
            return {}

    def get_item(self, item_id: str) -> Item:
        return self._items.get(item_id)

    def get_items(self) -> List[Item]:
        return list(self._items.values())

    def has_item(self, item_id: str) -> bool:
        return item_id in self._items
