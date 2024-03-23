from typing import List

from db import DB
from schemas.crossword import Crossword


class CrosswordService:
    """
    Service layer for interacting with and getting crosswords from the database
    """

    def __init__(self, db: DB):
        self.db = db

    def get_crossword(self, crossword_date: str) -> Crossword:
        if not self.db.has_crossword(crossword_date):
            raise ValueError(f"Crossword with date {crossword_date} does not exist")

        return self.db.get_crossword(crossword_date)

    def get_crosswords(self) -> List[Crossword]:
        return self.db.get_crosswords()

    def has_crossword(self, crossword_date: str) -> bool:
        return self.db.has_crossword(crossword_date)

    def add_crossword(self, crossword_date: str, score: int):
        if self.db.has_crossword(crossword_date):
            raise ValueError("Crossword already exists")

        crossword = Crossword(date=crossword_date, score=score)
        self.db.add_crossword(crossword)

    def delete_crossword(self, crossword_date: str):
        self.db.delete_crossword(crossword_date)
