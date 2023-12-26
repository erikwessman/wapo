from dataclasses import dataclass


@dataclass
class Item:
    """
    Represents an inventory item
    """

    id: int
    name: str
    description: str
    one_time_use: bool
    price: int
    symbol: str
