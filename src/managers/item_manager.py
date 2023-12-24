from typing import List

from manager import Manager
from item import Item


class ItemManager(Manager):
    """
    """

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def get_items(self) -> List[Item]:
        data = self._read_data()
        return data.values()

    def get_item(self, item_id: int) -> Item:
        data = self._read_data()
        return data[item_id]

    def item_exists(self, item_id: int) -> bool:
        data = self._read_data()
        return item_id in data
