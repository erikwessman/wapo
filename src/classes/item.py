class Item:
    """"""

    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        one_time_use: bool,
        price: int,
        symbol: str,
    ):
        self._id = id
        self._title = name
        self._description = description
        self._one_time_use = one_time_use
        self._price = price
        self._symbol = symbol

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def one_time_use(self) -> bool:
        return self._one_time_use

    @property
    def price(self) -> int:
        return self._price

    @property
    def symbol(self) -> str:
        return self._symbol

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
