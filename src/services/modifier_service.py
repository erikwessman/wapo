from typing import List
import json

from db import DB
from schemas.store_modifier import StoreModifier


class ModifierService:
    """
    Service layer for interacting with and getting modifiers from the database
    """

    def __init__(self, db: DB):
        self.db = db
        self.delete_modifiers()
        self._load_items()

    def _load_modifiers(self, modifiers_path: str):
        try:
            with open(modifiers_path, "r") as file:
                raw_data = json.load(file)
                self.add_modifier(raw_data)
        except FileNotFoundError:
            raise ValueError(f"The file '{modifiers_path}' was not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Could not decode the contents of '{modifiers_path}'")

    def get_modifier(self, modifier_id: str) -> StoreModifier:
        if not self.db.has_modifier(modifier_id):
            raise ValueError(f"Modifier with ID {modifier_id} does not exist")

        return self.db.get_modifier(modifier_id)

    def get_modifiers(self) -> List[StoreModifier]:
        return self.db.get_modifiers()

    def has_modifier(self, modifier_id: str) -> bool:
        return self.db.has_modifier(modifier_id)

    def add_modifier(self, modifier_dict: dict):
        modifier = StoreModifier(**modifier_dict)

        if self.db.has_modifier(modifier.id):
            raise ValueError("Modifier already exists")

        modifier = StoreModifier()
        self.db.add_modifier(modifier)

    def delete_modifier(self, modifier_id: str):
        self.db.delete_modifier(modifier_id)

    def delete_modifiers(self):
        self.db.delete_modifiers()
