import os
import sys
from typing import List
from urllib.parse import quote_plus
from dataclasses import asdict
import pymongo

from classes.player import Player
from classes.crossword import Crossword
from classes.roulette import Roulette


class DB:
    """
    PyMongo database instance and methods
    """

    def __init__(self, db_name: str = None):
        self.client = self.connect()
        self.database = self.client[db_name]

        self.player_collection = self.database["players"]
        self.crossword_collection = self.database["crosswords"]
        self.roulette_collection = self.database["roulette"]

    def __del__(self):
        self.client.close()

    # --- General methods ---

    @staticmethod
    def connect():
        db_host = os.getenv("MONGO_HOST") or "localhost"
        db_user = os.getenv("MONGO_USER") or None
        db_pass = os.getenv("MONGO_PASS") or None

        if db_user:
            db_user_quote = quote_plus(db_user)
            db_pass_quote = quote_plus(db_pass)
            mongo_uri = (
                f"mongodb+srv://{db_user_quote}:{db_pass_quote}@{db_host}"
                "/?retryWrites=true&w=majority"
            )
        else:
            mongo_uri = f"mongodb://{db_host}/?retryWrites=true&w=majority"

        print(f"Attempting to connect to database at {mongo_uri}")
        try:
            client = pymongo.MongoClient(mongo_uri)
            client.server_info()
            print("Connected to database")
        except Exception as error:
            print(f"Unable to connect to database: {error}")
            sys.exit(1)

        return client

    def clear_database(self) -> None:
        self.delete_all_players()
        self.delete_all_crosswords()
        self.delete_all_roulettes()

    def get_size_mb(self) -> float:
        stats = self.database.command("dbstats", scale=1024 * 1024)
        return stats["dataSize"]

    # --- Player helper methods ---

    def get_player(self, player_id: int) -> Player:
        player_data = self.player_collection.find_one({"id": player_id})
        if player_data:
            player_data.pop("_id", None)
            return Player(**player_data)
        return None

    def get_players(self, skip: int = 0, limit: int = 0) -> List[Player]:
        players = self.player_collection.find({}).skip(skip).limit(limit)
        return [
            Player(**{k: v for k, v in player_data.items() if k != "_id"})
            for player_data in players
        ]

    def add_player(self, player: Player) -> str:
        player_dict = asdict(player)
        return self.player_collection.insert_one(player_dict).inserted_id

    def update_player(self, player: Player):
        player_dict = asdict(player)
        self.player_collection.update_one({"id": player.id}, {"$set": player_dict})

    def has_player(self, player_id: int):
        return self.player_collection.count_documents({"id": player_id}) > 0

    def delete_player(self, player_id: int) -> None:
        self.player_collection.delete_one({"id": player_id})

    def delete_all_players(self):
        self.player_collection.delete_many({})

    # --- Crosswor helper methods ---

    def get_crossword(self, crossword_date: str) -> Crossword:
        crossword_data = self.crossword_collection.find_one({"date": crossword_date})
        if crossword_data:
            crossword_data.pop("_id", None)
            return Crossword(**crossword_data)
        return None

    def get_crosswords(self, skip: int = 0, limit: int = 0) -> List[Crossword]:
        crosswords = self.crossword_collection.find({}).skip(skip).limit(limit)
        return [
            Crossword(**{k: v for k, v in crossword_data.items() if k != "_id"})
            for crossword_data in crosswords
        ]

    def add_crossword(self, crossword: Crossword) -> str:
        crossword_dict = asdict(crossword)
        return self.crossword_collection.insert_one(crossword_dict).inserted_id

    def update_crossword(self, crossword: Crossword) -> None:
        crossword_dict = asdict(crossword)
        self.crossword_collection.update_one(
            {"date": crossword.date}, {"$set": crossword_dict}
        )

    def has_crossword(self, crossword_date: str) -> bool:
        return self.crossword_collection.count_documents({"date": crossword_date}) > 0

    def delete_crossword(self, crossword_date: str) -> None:
        self.crossword_collection.delete_one({"date": crossword_date})

    def delete_all_crosswords(self):
        self.crossword_collection.delete_many({})

    # --- Roulette helper methods ---

    def get_roulette(self, id: str) -> Roulette:
        roulette_data = self.roulette_collection.find_one({"id": id})
        if roulette_data:
            roulette_data.pop("_id", None)
            return Roulette(**roulette_data)
        return None

    def get_roulettes(self, skip: int = 0, limit: int = 0) -> List[Roulette]:
        roulettes = self.roulette_collection.find({}).skip(skip).limit(limit)
        return [
            Roulette(**{k: v for k, v in roulette_data.items() if k != "_id"})
            for roulette_data in roulettes
        ]

    def add_roulette(self, roulette: Roulette) -> str:
        roulette_dict = asdict(Roulette)
        return self.roulette_collection.insert_one(roulette_dict).inserted_id

    def update_roulette(self, roulette: Roulette) -> None:
        roulette_dict = asdict(roulette)
        self.roulette_collection.update_one(
            {"id": roulette.id}, {"$set": roulette_dict}
        )

    def has_roulette(self, id: str) -> bool:
        return self.roulette_collection.count_documents({"id": id}) > 0

    def delete_roulette(self, id: str) -> None:
        self.roulette_collection.delete_one({"id": id})

    def delete_all_roulettes(self):
        self.roulette_collection.delete_many({})
