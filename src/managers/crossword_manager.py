from typing import Dict, List

from base_manager import Manager
from classes.crossword import Crossword


class CrosswordManager(Manager):
    """
    Manages completed crosswords persistently
    """

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def _read_data(self) -> Dict[str, Crossword]:
        raw_data = super()._read_data()
        return {key: Crossword.from_dict(item_data) for key, item_data in raw_data.items()}

    def _write_data(self, data) -> None:
        data = {key: item.__dict__ for key, item in data.items()}
        super()._write_data(data)

    def save_crossword(self, crossword_date: str) -> None:
        data = self._read_data()
        data[crossword_date] = Crossword(crossword_date, 0)
        self._write_data(data)

    def get_crosswords(self) -> List[str]:
        data = self._read_data()
        return list(data.values())

    def get_crossword(self, crossword_date) -> Crossword:
        data = self._read_data()
        return data[crossword_date]

    def has_crossword(self, crossword_date) -> bool:
        data = self._read_data()
        return crossword_date in data
