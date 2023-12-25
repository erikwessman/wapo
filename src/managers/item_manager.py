from typing import List, Dict

from managers.base_manager import Manager
from classes.item import Item


class ItemManager(Manager):
    """"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self._items = self._read_data()

    def _read_data(self) -> Dict[str, Item]:
        raw_data = super()._read_data()
        return {key: Item.from_dict(item_data) for key, item_data in raw_data.items()}

    def save_data(self) -> None:
        data = {key: item.__dict__ for key, item in self._items.items()}
        super()._write_data(data)

    def get_items(self) -> List[Item]:
        return self._items.values()

    def get_item(self, item_id: int) -> Item:
        return self._items[item_id]

    def has_item(self, item_id: int) -> bool:
        return item_id in self._items
