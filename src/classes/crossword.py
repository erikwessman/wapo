class Crossword:
    """"""

    def __init__(self, date: str, score: int):
        self._date = date
        self._score = score

    @property
    def date(self) -> str:
        return self._date

    @property
    def score(self) -> int:
        return self._score

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
