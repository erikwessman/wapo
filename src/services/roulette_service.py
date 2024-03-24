from typing import Dict, List

from db import DB
from schemas.roulette import Roulette


class RouletteService:
    """
    Service layer for geting and interacting with Roulette objects from the db
    """

    def __init__(self, db: DB):
        self.db = db

    def get_roulettes(self) -> List[Roulette]:
        return self.db.get_roulettes()

    def get_roulettes_by_player(self, player_id: int) -> List[Roulette]:
        return self.db.get_roulettes_by_player(player_id)

    def add_roulette(self, date, players: Dict[str, int], winner: int):
        roulette = Roulette(date=date, players=players, winner=winner)
        self.db.add_roulette(roulette)

    def get_roulette_stats_by_player(self, player_id: int) -> str:
        roulettes = self.get_roulettes_by_player(player_id)
        total_bet = 0
        total_win = 0
        max_win = 0
        max_loss = 0

        if not roulettes:
            return "No Roulette data"

        for roulette in roulettes:
            player_bet = roulette.players.get(str(player_id), 0)
            total_bet += player_bet

            if roulette.winner == player_id:
                total_pool = sum(roulette.players.values()) - player_bet
                total_win += total_pool
                max_win = max(max_win, total_pool)
            else:
                max_loss = max(max_loss, player_bet)

        return (
            f"Total bet: {total_bet}\n"
            f"Total win: {total_win}\n"
            f"Biggest win: {max_win}\n"
            f"Biggest loss: {max_loss}"
        )
