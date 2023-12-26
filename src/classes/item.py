from dataclasses import dataclass


@dataclass
class Item:
    """"""

    id: int
    name: str
    description: str
    one_time_use: bool
    price: int
    symbol: str
