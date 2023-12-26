from dataclasses import dataclass


@dataclass
class Crossword:
    """
    Represents a crossword puzzle with its completion date and score.
    """

    date: str
    score: int
