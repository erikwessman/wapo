from typing import List

from db import DB
from classes.crossword import Crossword


class CrosswordService:
    """"""

    def __init__(self, db: DB):
        self.db = db

    def save_crossword(self, crossword_date: str, score: int = 0) -> Crossword:
        if self.db.has_crossword(crossword_date):
            raise ValueError("Crossword already exists")

        crossword = Crossword(crossword_date, score)
        self.db.add_crossword(crossword)
        return crossword

    def get_crossword(self, crossword_date) -> Crossword:
        return self.db.get_crossword(crossword_date)

    def get_crosswords(self) -> List[Crossword]:
        return self.db.get_crosswords()

    def has_crossword(self, crossword_date) -> bool:
        return self.db.has_crossword(crossword_date)
