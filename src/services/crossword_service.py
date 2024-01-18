from typing import List
from discord.ext.commands import BadArgument

from db import DB
from schemas.crossword import Crossword


class CrosswordService:
    """
    Service layer for interacting with and getting crosswords from the database
    """

    def __init__(self, db: DB):
        self.db = db

    def save_crossword(self, crossword_date: str, score: int = 0) -> Crossword:
        if self.db.has_crossword(crossword_date):
            raise BadArgument("Crossword already exists")

        crossword = Crossword(date=crossword_date, score=score)
        self.db.add_crossword(crossword)
        return crossword

    def get_crossword(self, crossword_date) -> Crossword:
        if not self.db.has_crossword(crossword_date):
            raise BadArgument(f"Crossword with date {crossword_date} does not exist")

        return self.db.get_crossword(crossword_date)

    def get_crosswords(self) -> List[Crossword]:
        return self.db.get_crosswords()

    def has_crossword(self, crossword_date) -> bool:
        return self.db.has_crossword(crossword_date)
