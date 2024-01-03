from dataclasses import dataclass


@dataclass
class Holding:
    """
    Represents a players holding
    """

    ticker: str
    shares: int
    average_price: float
