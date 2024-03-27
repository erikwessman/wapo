from typing import List
import json

from helper import closest_match
from db import DB
from schemas.item import Item


class ItemService:
    """
    Service layer for interacting with and getting items from the database
    """

    def __init__(self, db: DB, items_path: str):
        self.db = db
        self.delete_items()
        self._load_items(items_path)

    def _load_items(self, items_path: str):
        try:
            with open(items_path, "r") as file:
                raw_data = json.load(file)
                for item_dict in raw_data:
                    self.add_item(item_dict)
        except FileNotFoundError:
            raise ValueError(f"The file '{items_path}' was not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Could not decode the contents of '{items_path}'")

    def get_item(self, item_id: str) -> Item:
        if not self.db.has_item(item_id):
            raise ValueError(f"Item with ID {item_id} does not exist")

        return self.db.get_item(item_id)

    def get_items(self) -> List[Item]:
        return self.db.get_items()

    def get_purchasable_items(self) -> List[Item]:
        return [item for item in self.db.get_items() if item.is_purchasable]

    def has_item(self, item_id: str) -> bool:
        return self.db.has_item(item_id)

    def add_item(self, item_dict: dict):
        item = Item(**item_dict)

        if self.db.has_item(item.id):
            raise ValueError("Item already exists")

        self.db.add_item(item)

    def delete_item(self, item_id: str):
        self.db.delete_item(item_id)

    def delete_items(self):
        self.db.delete_all_items()

    def get_item_by_name(self, item_name: str, fuzzy_match: bool = True) -> Item:
        if fuzzy_match:
            all_item_names = [i.name for i in self.get_items()]
            item_name = closest_match(item_name, all_item_names)

        for item in self.get_items():
            if item.name == item_name:
                return item

        raise ValueError("Item not found")
