from dataclasses import dataclass


@dataclass
class StockPrice:
    """
    Represents a stock price
    """

    ticker: str
    timestamp: str
    price: int
