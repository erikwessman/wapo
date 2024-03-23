from typing import List

from db import DB
from schemas.horse_race import HorseRace


class HorseRaceService:
    """
    Service layer for geting and interacting with horse race from the db
    """

    def __init__(self, db: DB):
        self.db = db

    def get_horse_races(self) -> List[HorseRace]:
        return self.db.get_horse_races()

    def get_player_horse_races(self, player_id: int) -> List[HorseRace]:
        return self.db.get_horse_races_by_player(player_id)

    def add_horse_race(self, date, player: int, bet: int, win: int):
        horse_race = HorseRace(date=date, player=player, bet=bet, win=win)
        self.db.add_horse_race(horse_race)

    def get_horse_race_stats_by_player(self, player_id: int) -> str:
        horse_races = self.get_player_horse_races(player_id)
        if horse_races:
            total_bet = sum(h.bet for h in horse_races)
            total_win = sum(h.win for h in horse_races)
            max_win = max(max((h.win - h.bet) for h in horse_races), 0)
            max_loss = max(max((h.bet - h.win) for h in horse_races), 0)

            return (
                f"Total bet: {total_bet}\n"
                f"Total win: {total_win}\n"
                f"Biggest win: {max_win}\n"
                f"Biggest loss: {max_loss}"
            )
        else:
            return "No Horse Race data"
