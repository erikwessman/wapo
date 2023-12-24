from typing import List, Dict

from base_manager import Manager
from classes.item import Item


class ItemManager(Manager):
    """"""

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def _read_data(self) -> Dict[str, Item]:
        raw_data = super()._read_data()
        return {key: Item.from_dict(item_data) for key, item_data in raw_data.items()}

    def _write_data(self, data) -> None:
        data = {key: item.__dict__ for key, item in data.items()}
        super()._write_data(data)

    def get_items(self) -> List[Item]:
        data = self._read_data()
        return data.values()

    def get_item(self, item_id: int) -> Item:
        data = self._read_data()
        return data[item_id]

    def has_item(self, item_id: int) -> bool:
        data = self._read_data()
        return item_id in data
