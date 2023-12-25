class Item:
    """"""

    def __init__(
        self,
        item_id: int,
        title: str,
        description: str,
        one_time_use: bool,
        price: int,
        symbol: str,
    ):
        self._item_id = item_id
        self._title = title
        self._description = description
        self._one_time_use = one_time_use
        self._price = price
        self._symbol = symbol

    @property
    def item_id(self) -> int:
        return self._item_id

    @property
    def title(self) -> str:
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
