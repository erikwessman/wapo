import os
import datetime
import logging
from urllib.parse import quote_plus
from typing import List
from mongoengine import connect

from schemas.player import Player
from schemas.crossword import Crossword
from schemas.roulette import Roulette
from schemas.horse_race import HorseRace
from schemas.stock import Stock
from schemas.stock_price import StockPrice
from schemas.store_item import StoreItem
from schemas.store_modifier import StoreModifier


class DB:
    """
    MongoEngine database instance and methods
    """

    def __init__(self, db_name: str = None):
        self.client = self.connect(db_name)

    @staticmethod
    def connect(db_name: str = None):
        db_host = os.getenv("MONGO_HOST") or "mongo"
        db_user = os.getenv("MONGO_USER") or None
        db_pass = os.getenv("MONGO_PASS") or None

        if db_user:
            db_user_quote = quote_plus(db_user)
            db_pass_quote = quote_plus(db_pass)
            mongo_uri = f"mongodb+srv://{db_user_quote}:{db_pass_quote}@{db_host}"
        else:
            mongo_uri = f"mongodb://{db_host}"

        logging.info(f"Connecting to database host {db_host}...")
        connect(db_name, host=mongo_uri)

    # --- Player helper methods ---

    def get_player(self, player_id: int) -> Player:
        return Player.objects(id=player_id).first()

    def get_players(self, skip: int = 0, limit: int = 0) -> List[Player]:
        return list(Player.objects.skip(skip).limit(limit))

    def add_player(self, player: Player) -> str:
        player.save()
        return str(player.id)

    def has_player(self, player_id: int) -> bool:
        return Player.objects(id=player_id).count() > 0

    def delete_player(self, player_id: int) -> None:
        Player.objects(id=player_id).delete()

    def delete_all_players(self):
        Player.objects.delete()

    # --- Item helper methods ---

    def get_item(self, item_id: str) -> StoreItem:
        return StoreItem.objects(id=item_id).first()

    def get_items(self, skip: int = 0, limit: int = 0) -> List[StoreItem]:
        return list(StoreItem.objects.skip(skip).limit(limit))

    def add_item(self, item: StoreItem) -> str:
        item.save()
        return str(item.id)

    def has_item(self, item_id: str) -> bool:
        return StoreItem.objects(id=item_id).count() > 0

    def delete_item(self, item_id: str) -> None:
        StoreItem.objects(id=item_id).delete()

    def delete_all_items(self):
        StoreItem.objects.delete()

    # --- Modifier helper methods ---

    def get_modifier(self, modifier_id: str) -> StoreModifier:
        return StoreModifier.objects(id=modifier_id).first()

    def get_modifiers(self, skip: int = 0, limit: int = 0) -> List[StoreModifier]:
        return list(StoreModifier.objects.skip(skip).limit(limit))

    def add_modifier(self, modifier: StoreModifier) -> str:
        modifier.save()
        return str(modifier.id)

    def has_modifier(self, modifier_id: str) -> bool:
        return StoreModifier.objects(id=modifier_id).count() > 0

    def delete_modifier(self, modifier_id: str) -> None:
        StoreModifier.objects(id=modifier_id).delete()

    def delete_all_modifiers(self):
        StoreModifier.objects.delete()

    # --- Crossword helper methods ---

    def get_crossword(self, crossword_date: str) -> Crossword:
        return Crossword.objects(date=crossword_date).first()

    def get_crosswords(self, skip: int = 0, limit: int = 0) -> List[Crossword]:
        return list(Crossword.objects.skip(skip).limit(limit))

    def add_crossword(self, crossword: Crossword) -> str:
        crossword.save()
        return str(crossword.id)

    def has_crossword(self, crossword_date: str) -> bool:
        return Crossword.objects(date=crossword_date).count() > 0

    def delete_crossword(self, crossword_date: str) -> None:
        Crossword.objects(date=crossword_date).delete()

    def delete_all_crosswords(self):
        Crossword.objects.delete()

    # --- Roulette helper methods ---

    def get_roulettes(self, skip: int = 0, limit: int = 0) -> List[Roulette]:
        return list(Roulette.objects.skip(skip).limit(limit))

    def get_roulettes_by_player(
        self, player_id: int, skip: int = 0, limit: int = 0
    ) -> List[Roulette]:
        query = {f"players.{player_id}": {"$exists": True}}
        return list(Roulette.objects(__raw__=query).skip(skip).limit(limit))

    def add_roulette(self, roulette: Roulette) -> str:
        roulette.save()
        return str(roulette.id)

    def delete_all_roulettes(self):
        Roulette.objects.delete()

    # --- HorseRace helper methods ---

    def get_horse_races(self, skip: int = 0, limit: int = 0) -> List[HorseRace]:
        return list(HorseRace.objects.skip(skip).limit(limit))

    def get_horse_races_by_player(
        self, player_id: int, skip: int = 0, limit: int = 0
    ) -> List[HorseRace]:
        return list(HorseRace.objects(player=player_id).skip(skip).limit(limit))

    def add_horse_race(self, horse_race: HorseRace) -> str:
        horse_race.save()
        return str(horse_race.id)

    def delete_all_horse_races(self):
        HorseRace.objects.delete()

    # --- Stock helper methods ---

    def get_stock(self, ticker: str) -> Stock:
        return Stock.objects(ticker=ticker).first()

    def get_stocks(self, skip: int = 0, limit: int = 0) -> List[Stock]:
        return list(Stock.objects.skip(skip).limit(limit))

    def add_stock(self, stock: Stock) -> str:
        stock.save()
        return str(stock.id)

    def update_stock(self, stock: Stock) -> None:
        Stock.objects(ticker=stock.ticker).update_one(**stock.to_mongo())

    def has_stock(self, ticker: str) -> bool:
        return Stock.objects(ticker=ticker).count() > 0

    def delete_stock(self, ticker: str) -> None:
        Stock.objects(ticker=ticker).delete()

    def delete_all_stocks(self):
        Stock.objects.delete()

    # --- StockPrice helper methods ---

    def get_current_stock_price(self, ticker: str) -> StockPrice:
        return StockPrice.objects(ticker=ticker).order_by("-timestamp").first()

    def get_stock_price_by_date(
        self, ticker: str, date: datetime.datetime
    ) -> StockPrice:
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        return StockPrice.objects(
            ticker=ticker, timestamp__gte=start_date, timestamp__lte=end_date
        ).first()

    def get_stock_price_in_date_range(
        self, ticker: str, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> List[StockPrice]:
        return list(
            StockPrice.objects(
                ticker=ticker, timestamp__gte=start_date, timestamp__lte=end_date
            )
        )

    def get_stock_price_history(self, ticker: str) -> List[StockPrice]:
        return list(StockPrice.objects(ticker=ticker).order_by("timestamp"))

    def has_stock_price(self, ticker: str) -> bool:
        return StockPrice.objects(ticker=ticker).count() > 0

    def add_stock_price(self, stock_price: StockPrice) -> str:
        stock_price.save()
        return str(stock_price.id)

    def delete_all_stock_prices(self):
        StockPrice.objects.delete()
