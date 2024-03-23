from typing import List

from db import DB
from schemas.player import Player


class PlayerService:
    """
    Service layer for interacting with and getting players from the database
    """

    def __init__(self, db: DB):
        self.db = db

    def get_player(self, player_id: int) -> Player:
        if not self.db.has_player(player_id):
            return self.add_player(player_id)

        return self.db.get_player(player_id)

    def get_players(self) -> List[Player]:
        return self.db.get_players()

    def has_player(self, player_id: int) -> Player:
        return self.db.has_player(player_id)

    def add_player(self, player_id: int) -> Player:
        if self.db.has_player(player_id):
            raise ValueError("Player already exists")

        player = Player(id=player_id)
        self.db.add_player(player)
        return player

    def delete_player(self, player_id: int):
        self.db.delete_player(player_id)
