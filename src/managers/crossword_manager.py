from typing import List

from manager import Manager


class CrosswordManager(Manager):
    """
    Manages completed crosswords persistently
    """

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def save_crossword(self, crossword_date: str) -> None:
        data = self._read_data()

        data[crossword_date] = True

        self._write_data(data)

    def get_crosswords(self) -> List[str]:
        data = self._read_data()

        return list(data.keys())

    def has_crossword(self, crossword_date) -> bool:
        data = self._read_data()
        return crossword_date in data
