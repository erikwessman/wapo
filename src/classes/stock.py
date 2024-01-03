from dataclasses import dataclass


@dataclass
class Stock:
    """
    Represents a single company stock
    """

    ticker: str
    company: str
