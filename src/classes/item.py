class Item:
    """"""

    def __init__(
        self, item_id: int, title: str, description: str, one_time_use: bool, price: int
    ):
        self._item_id = item_id
        self._title = title
        self._description = description
        self._one_time_use = one_time_use
        self._price = price

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

    def __str__(self):
        return (
            f"Item ID: {self._item_id}, "
            f"Title: {self._title}, "
            f"Description: {self._description}, "
            f"One Time Use: {self._one_time_use} "
            f"Price: {self._price}"
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
