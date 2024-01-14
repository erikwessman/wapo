from .blackjack_models import GameState
from .blackjack_impl import BlackjackImpl


class Blackjack:
    """
    One instance per game. 1 player only.
    """

    _RULES = """
        House Rules:
            - Player is dealt 2 cards
            - Dealer is dealt 1 card
            - Player can hit or stand, no other options
            - Once player stands, dealer plays
            - Dealer stands on 17

            Win conditions:
            - Player wins if:
                - Player's total is closer to 21 than the dealer's total.
                - Dealer's total exceeds 21 (dealer busts) and the player does not bust.
            - Dealer wins if:
                - Dealer's total is closer to 21 than the player's total.
                - Player's total exceeds 21 (player busts).
            - It's a tie if:
                - Both player and dealer have the same total.
                - Both player and dealer hit 21.
    """

    def __init__(self) -> None:
        self.game: BlackjackImpl = BlackjackImpl()

    def get_rules(self) -> str:
        return self._RULES

    def deal_cards(self) -> None:
        self.game.deal_cards()

    def hit(self) -> None:
        self.game.player_hit()

    def stand(self) -> None:
        self.game.player_stand()

    def display(self) -> str:
        return self.game.display()

    def is_bust(self) -> bool:
        return self.game.player_is_bust()

    def get_state(self) -> GameState:
        return self.game._game_state
