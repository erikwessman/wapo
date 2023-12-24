import json

from item import Item


class Store:
    def __init__(self, file_path: str):
        self._items = []
        self._load_items(file_path)

    @property
    def items(self):
        return self.items

    def _load_items(self, file_path):
        try:
            with open(file_path, "r") as file:
                items_data = json.load(file)
                for item in items_data:
                    self._items.append(
                        Item(
                            item_id=item["item_id"],
                            title=item["title"],
                            description=item["description"],
                            one_time_use=item["one_time_use"],
                        )
                    )
        except FileNotFoundError:
            print("File not found.")
        except json.JSONDecodeError:
            print("Error parsing JSON.")
