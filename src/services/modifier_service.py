from typing import List
import json

from helper import closest_match
from db import DB
from schemas.modifier import Modifier


class ModifierService:
    """
    Service layer for interacting with and getting modifiers from the database
    """

    def __init__(self, db: DB, modifiers_path: str):
        self.db = db
        self.delete_modifiers()
        self._load_modifiers(modifiers_path)

    def _load_modifiers(self, modifiers_path: str):
        try:
            with open(modifiers_path, "r") as file:
                raw_data = json.load(file)
                for modifier_dict in raw_data:
                    self.add_modifier(modifier_dict)
        except FileNotFoundError:
            raise ValueError(f"The file '{modifiers_path}' was not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Could not decode the contents of '{modifiers_path}'")

    def get_modifier(self, modifier_id: str) -> Modifier:
        if not self.db.has_modifier(modifier_id):
            raise ValueError(f"Modifier with ID {modifier_id} does not exist")

        return self.db.get_modifier(modifier_id)

    def get_modifiers(self) -> List[Modifier]:
        return self.db.get_modifiers()

    def get_purchasable_modifiers(self) -> List[Modifier]:
        return [modifier for modifier in self.db.get_modifiers() if modifier.is_purchasable]

    def has_modifier(self, modifier_id: str) -> bool:
        return self.db.has_modifier(modifier_id)

    def add_modifier(self, modifier_dict: dict):
        modifier = Modifier(**modifier_dict)

        if self.db.has_modifier(modifier.id):
            raise ValueError("Modifier already exists")

        self.db.add_modifier(modifier)

    def delete_modifier(self, modifier_id: str):
        self.db.delete_modifier(modifier_id)

    def delete_modifiers(self):
        self.db.delete_all_modifiers()

    def get_modifier_by_name(
        self, modifier_name: str, fuzzy_match: bool = True
    ) -> Modifier:
        if fuzzy_match:
            all_modifier_names = [i.name for i in self.get_modifiers()]
            modifier_name = closest_match(modifier_name, all_modifier_names)

        for modifier in self.get_modifiers():
            if modifier.name == modifier_name:
                return modifier

        raise ValueError("Modifier not found")
