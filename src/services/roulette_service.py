import uuid
import time

from db import DB
from classes.roulette import Roulette


class RouletteService:
    """
    Service layer for geting and interacting with Roulette objects from the db
    """

    def __init__(self, db: DB):
        self.db = db

    def add_roulette(self, roulette_id: int) -> Roulette:
        if self.db.has_roulette(roulette_id):
            raise ValueError("Roulette already exists")

        roulette = Roulette(id=uuid.uuid4(), timestamp=time.time())
        self.db.add_roulette(roulette)
        return roulette
