import json
import datetime
from typing import List

from db import DB
from classes.stock import Stock
from classes.stock_price import StockPrice
from stock_sim import StockSim


class StockService:
    """
    Service layer for geting and interacting with Stock and Stock
    Price objects from the db
    """

    def __init__(self, db: DB):
        self.db = db
        self.stock_sim = StockSim()
        self.handle_initialize_stocks()

    def handle_initialize_stocks(self):
        """
        Looks at the stocks.json file and initializes the database with data

        If the stock does not exist, create an entry for it
        If the stock prices do not exist, simulate some initial prices
        """

        with open("data/stocks.json", "r") as file:
            data = json.load(file)

            for stock_dict in data:
                company = stock_dict["company"]
                ticker = stock_dict["ticker"]
                real_ticker = stock_dict["real_ticker"]

                if not self.has_stock(ticker):
                    print(f"Adding stock information for {company}")
                    self.add_stock(ticker, company)

                if not self.has_stock_price(ticker):
                    print(f"Adding initial batch of stock prices for {company}")
                    stock_prices_df = self.stock_sim.simulate_initial_stock_prices(
                        real_ticker
                    )
                    stock_prices = self.stock_sim.dataframe_to_stock_prices(
                        ticker, stock_prices_df
                    )
                    for stock_price in stock_prices:
                        self.db.add_stock_price(stock_price)

    def get_stock_price_plot(self, stock: Stock, stock_prices: List[StockPrice]):
        if not stock_prices:
            raise ValueError("No data to plot")

        return self.stock_sim.plot_stock_prices(stock, stock_prices)

    def simulate_next_stock_prices(self, ticker: str):
        curr_stock_prices = self.get_stock_prices(ticker)
        curr_stock_prices_df = self.stock_sim.stock_prices_to_dataframe(
            curr_stock_prices
        )

        next_stock_prices_df = self.stock_sim.simulate_next_stock_price(
            curr_stock_prices_df
        )
        next_stock_prices = self.stock_sim.dataframe_to_stock_prices(
            ticker, next_stock_prices_df
        )

        for stock_price in next_stock_prices:
            self.db.add_stock_price(stock_price)

    def get_stock(self, ticker) -> Stock:
        return self.db.get_stock(ticker)

    def get_all_stocks(self) -> List[Stock]:
        return self.db.get_stocks()

    def has_stock(self, ticker: str) -> bool:
        return self.db.has_stock(ticker)

    def has_stock_price(self, ticker: str) -> bool:
        return self.db.has_stock_price(ticker)

    def get_current_stock_price(self, ticker: str) -> float:
        return self.db.get_current_stock_price(ticker).price

    def get_stock_price_by_date(self, ticker: str, date: datetime) -> float:
        return self.db.get_stock_price_by_date(ticker, date).price

    def get_stock_price_in_date_range(
        self, ticker: str, start_date: datetime, end_date: datetime
    ) -> List[StockPrice]:
        return self.db.get_stock_price_in_date_range(ticker, start_date, end_date)

    def get_stock_prices(self, ticker: str) -> List[StockPrice]:
        return self.db.get_stock_price_history(ticker)

    def add_stock(self, ticker: str, company: str):
        if self.db.has_stock(ticker):
            raise ValueError("Stock with this ticker already exists")

        stock = Stock(ticker=ticker, company=company)
        self.db.add_stock(stock)
