from typing import List
from prettytable import PrettyTable
from .blackjack_models import Card, CardRank, Deck, InvalidMove, GameState

# ########################################
# ||                                    ||
# ||  dont use me :), use blackjack.py  ||
# ||                                    ||
# ########################################


class BlackjackImpl:
    """
    Jackblack game implementation.
    Favor use of the Blackjack wrapper class instead of this one.
    """

    _has_dealt_cards: bool = False
    _game_state: GameState = GameState.IN_PROGRESS

    def __init__(self) -> None:
        self._deck: Deck = Deck()
        self.player_hand: list[Card] = []
        self.dealer_hand: list[Card] = []

    def deal_cards(self) -> None:
        """Deals two cards each to the player and the dealer."""
        if self._has_dealt_cards:
            raise InvalidMove("Cards have already been dealt")

        if self._game_state != GameState.IN_PROGRESS:
            raise InvalidMove("Game has already finished")

        self._has_dealt_cards = True

        self.player_hand.append(self._deck.draw_card())
        self.dealer_hand.append(self._deck.draw_card())
        self.player_hand.append(self._deck.draw_card())

    def player_stand(self) -> None:
        """Player decides to stand, finishing their turn and the dealer plays its turn."""

        if not self._has_dealt_cards:
            raise RuntimeError("Game has not started, initial cards needs to be dealt")

        if self._game_state != GameState.IN_PROGRESS:
            raise InvalidMove("Game has already finished")

        self._play_dealer_turn()

    def display(self) -> str:
        """Gets a string representing the current state of the game."""
        dealer_cards = ", ".join(str(card).split(" ")[0] for card in self.dealer_hand)
        player_cards = ", ".join(str(card).split(" ")[0] for card in self.player_hand)
        dealer_score = self._calculate_score(self.dealer_hand)
        player_score = self._calculate_score(self.player_hand)

        table = PrettyTable()
        table.field_names = ["Player", "Score", "Cards"]
        table.add_row(["Dealer", dealer_score, dealer_cards])
        table.add_row(["Player", f"-->{player_score}<--", player_cards])

        status_str = self._game_state.value.replace("_", " ").title()
        return f"||{status_str}||\n\n{table}"

    def player_is_bust(self) -> bool:
        """Returns True if the player is bust, else False."""
        return self._hand_is_bust(self.player_hand)

    def player_hit(self) -> None:
        self._hit_hand(self.player_hand)

        if self.player_is_bust():
            self._game_state = GameState.DEALER_WON

    def _hand_is_bust(self, hand: list[Card]) -> bool:
        """Returns True if the score is over 21, else False."""
        return self._calculate_score(hand) > 21

    def _hit_hand(self, hand: list[Card]) -> None:
        """Adds a card to the given hand."""

        if self._game_state != GameState.IN_PROGRESS:
            raise InvalidMove("Game has already finished")

        if not self._has_dealt_cards:
            raise InvalidMove("Game has not started, initial cards needs to be dealt")

        hand.append(self._deck.draw_card())

    def _calculate_score(self, hand: List[Card]) -> int:
        """Calculates and returns the score of a hand."""
        score = 0
        ace_count = 0
        for card in hand:
            if card.rank in [CardRank.JACK, CardRank.QUEEN, CardRank.KING]:
                score += 10
            elif card.rank == CardRank.ACE:
                ace_count += 1
                score += 11
            else:
                score += int(card.rank.value)

        while score > 21 and ace_count:
            score -= 10
            ace_count -= 1

        return score

    def _play_dealer_turn(self) -> None:
        """Executes the dealer's turn after the player stands."""

        if self._game_state != GameState.IN_PROGRESS:
            raise InvalidMove("Game has already finished")

        dealer_score = self._calculate_score(self.dealer_hand)

        # Dealer's turn
        while dealer_score < 17:
            self._hit_hand(self.dealer_hand)
            dealer_score = self._calculate_score(self.dealer_hand)

        player_score = self._calculate_score(self.player_hand)

        if player_score > 21:
            self._game_state = GameState.DEALER_WON
        elif dealer_score > 21:
            self._game_state = GameState.PLAYER_WON
        elif dealer_score > player_score:
            self._game_state = GameState.DEALER_WON
        elif dealer_score < player_score:
            self._game_state = GameState.PLAYER_WON
        else:
            self._game_state = GameState.DRAW
