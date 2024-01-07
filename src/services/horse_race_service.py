from typing import List

from db import DB
from schemas.horse_race import HorseRace


class HorseRaceService:
    """
    Service layer for geting and interacting with horse race from the db
    """

    def __init__(self, db: DB):
        self.db = db

    def add_horse_race(self, date, player: int, bet: int, win: int):
        horse_race = HorseRace(date=date, player=player, bet=bet, win=win)
        self.db.add_roulette(horse_race)

    def get_roulettes(self) -> List[HorseRace]:
        return self.db.get_horse()
