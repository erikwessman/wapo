from typing import Dict, List

from managers.base_manager import Manager
from classes.crossword import Crossword


class CrosswordManager(Manager):
    """"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self._crosswords = self._read_data()

    def _read_data(self) -> Dict[str, Crossword]:
        raw_data = super()._read_data()
        return {
            key: Crossword.from_dict(item_data) for key, item_data in raw_data.items()
        }

    def save_data(self) -> None:
        data = {key: item.__dict__ for key, item in self._crosswords.items()}
        super()._write_data(data)

    def save_crossword(self, crossword_date: str) -> None:
        self._crosswords[crossword_date] = Crossword(crossword_date, 0)

    def get_crosswords(self) -> List[Crossword]:
        return self._crosswords.values()

    def get_crossword(self, crossword_date) -> Crossword:
        return self._crosswords[crossword_date]

    def has_crossword(self, crossword_date) -> bool:
        return crossword_date in self._crosswords
