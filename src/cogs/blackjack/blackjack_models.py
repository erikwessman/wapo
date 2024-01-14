from enum import Enum
import random


class InvalidMove(Exception):
    pass


class GameState(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    PLAYER_WON = "PLAYER_WON"
    DEALER_WON = "DEALER_WON"
    DRAW = "DRAW"


class Suite(Enum):
    HEARTS = "HEARTS"
    DIAMONDS = "DIAMONDS"
    CLUBS = "CLUBS"
    SPADES = "SPADES"


class CardRank(Enum):
    CARD_2 = "2"
    CARD_3 = "3"
    CARD_4 = "4"
    CARD_5 = "5"
    CARD_6 = "6"
    CARD_7 = "7"
    CARD_8 = "8"
    CARD_9 = "9"
    CARD_10 = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

    def __str__(self):
        return f"{self.value}"


class Card:
    """Represents a playing card with a suit and a rank."""

    RANKS: list[CardRank] = [
        CardRank.CARD_2,
        CardRank.CARD_3,
        CardRank.CARD_4,
        CardRank.CARD_5,
        CardRank.CARD_6,
        CardRank.CARD_7,
        CardRank.CARD_8,
        CardRank.CARD_9,
        CardRank.CARD_10,
        CardRank.JACK,
        CardRank.QUEEN,
        CardRank.KING,
        CardRank.ACE,
    ]

    def __init__(self, suit: Suite, rank: CardRank) -> None:
        if suit not in [Suite.HEARTS, Suite.DIAMONDS, Suite.CLUBS, Suite.SPADES]:
            raise ValueError("Invalid suit")

        if rank not in self.RANKS:
            raise ValueError("Invalid rank")

        self.suit = suit
        self.rank = rank

    def __repr__(self) -> str:
        return f"{self.rank} of {self.suit.value.title()}"


class Deck:
    """Represents a deck of playing cards."""

    def __init__(self) -> None:
        suits: list[Suite] = [Suite.HEARTS, Suite.CLUBS, Suite.DIAMONDS, Suite.SPADES]
        self._cards: list[Card] = [
            Card(suit, rank) for suit in suits for rank in Card.RANKS
        ]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self._cards)

    def draw_card(self) -> Card:
        """Draws and returns the top card from the deck."""
        return self._cards.pop()
