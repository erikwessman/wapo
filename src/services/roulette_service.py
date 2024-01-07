from typing import Dict, List

from db import DB
from schemas.roulette import Roulette


class RouletteService:
    """
    Service layer for geting and interacting with Roulette objects from the db
    """

    def __init__(self, db: DB):
        self.db = db

    def add_roulette(self, date, players: Dict[int, int], winner: int):
        roulette = Roulette(date=date, players=players, winner=winner)
        self.db.add_roulette(roulette)

    def get_roulettes(self) -> List[Roulette]:
        return self.db.get_roulettes()
