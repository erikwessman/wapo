import random
from enum import Enum
from typing import List


class DuelState(Enum):
    PENDING = 1
    ACCEPTED = 2
    COMPLETED = 3


class MoveType(Enum):
    ATTACK = "attack"
    DEFEND = "defend"
    HEAL = "heal"


class Duelist:
    max_health = 100

    def __init__(self, name: str, player_id: int, avatar: str = None):
        self.name = name
        self.id = player_id
        self.health = self.max_health
        self.avatar = avatar or "\U0001F476"
        self.is_shielded = False

    def take_damage(self, amount: int):
        if self.is_shielded:
            self.is_shielded = False
            return

        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def shield(self):
        self.is_shielded = True

    def is_defeated(self):
        return self.health <= 0


class DuelMove:
    def __init__(self, name: str, symbol: str, move_type: str, value: int, weight: int):
        self.name = name
        self.symbol = symbol
        self.move_type = move_type
        self.value = value
        self.weight = weight


class Duel:
    moves = [
        DuelMove("Sword", "⚔️", MoveType.ATTACK, 15, 10),
        DuelMove("Magic", "🔮", MoveType.ATTACK, 20, 8),
        DuelMove("Arrow", "🏹", MoveType.ATTACK, 12, 9),
        DuelMove("Fire", "🔥", MoveType.ATTACK, 25, 7),
        DuelMove("Ice", "❄️", MoveType.ATTACK, 18, 7),
        DuelMove("Poison", "☠️", MoveType.ATTACK, 22, 6),
        DuelMove("Lightning", "⚡", MoveType.ATTACK, 20, 8),
        DuelMove("Explosive", "💣", MoveType.ATTACK, 30, 5),
        DuelMove("Punch", "🥊", MoveType.ATTACK, 10, 12),
        DuelMove("Shield", "🛡️", MoveType.DEFEND, 0, 15),
        DuelMove("Psychic", "🌀", MoveType.ATTACK, 17, 9),
        DuelMove("Nature", "🌿", MoveType.ATTACK, 15, 10),
        DuelMove("Wind", "💨", MoveType.ATTACK, 13, 11),
        DuelMove("Water", "🌊", MoveType.ATTACK, 19, 8),
        DuelMove("Stealth", "🥷", MoveType.ATTACK, 25, 6),
        DuelMove("Robot", "🤖", MoveType.ATTACK, 20, 7),
        DuelMove("Heal", "💖", MoveType.HEAL, 20, 7),
    ]

    def __init__(self, challenger: Duelist, challengee: Duelist, wager: int):
        self.challenger = challenger
        self.challengee = challengee
        self.wager = wager
        self.state = DuelState.PENDING

    def accept(self):
        if self.state == DuelState.PENDING:
            self.state = DuelState.ACCEPTED

    def simulate(self):
        if self.state != DuelState.ACCEPTED:
            return ValueError("Duel has not been accepted")

        while not self.is_complete():
            yield self.do_round()

        self.state = DuelState.COMPLETED

    def do_round(self) -> str:
        attacker = random.choice([self.challenger, self.challengee])
        defender = self.challengee if attacker == self.challenger else self.challenger

        move = self.get_random_move(self.moves)
        shielded = defender.is_shielded

        if move.move_type == MoveType.ATTACK:
            defender.take_damage(move.value)
        elif move.move_type == MoveType.DEFEND:
            attacker.shield()
        elif move.move_type == MoveType.HEAL:
            attacker.heal(move.value)

        return self.generate_attack_message(attacker, defender, move, shielded)

    def generate_attack_message(
        self, attacker: Duelist, defender: Duelist, move: DuelMove, shielded: bool
    ) -> str:
        if move.move_type == MoveType.ATTACK:
            if shielded:
                move_details = f"{attacker.name} used {move.name} {move.symbol} for no damage because the attack was shielded!"
            else:
                move_details = f"{attacker.name} used {move.name} {move.symbol} for {move.value} damage!"
        elif move.move_type == MoveType.DEFEND:
            move_details = (
                f"{attacker.name} used {move.name} {move.symbol} to protect themselves!"
            )
        elif move.move_type == MoveType.HEAL:
            move_details = f"{attacker.name} used {move.name} {move.symbol} to heal for {move.value}!"

        arena = (
            f"{self.challenger.health}/{self.challenger.max_health} "
            f"{self.challenger.avatar}{'🛡️' if self.challenger.is_shielded else ''}"
            f"{'-' * 5} {move.symbol} {'-' * 5}"
            f" {'🛡️' if self.challengee.is_shielded else ''}{self.challengee.avatar} "
            f"{self.challengee.health}/{self.challengee.max_health}"
        )

        return "\n\n".join([move_details, arena])

    def generate_initial_message(self) -> str:
        details = (
            f"{self.challenger.health}/{self.challenger.max_health} {self.challenger.avatar}"
            f"{'-' * 11}"
            f"{self.challengee.avatar} {self.challengee.health}/{self.challengee.max_health}"
        )

        return details

    def is_complete(self) -> bool:
        return self.challenger.is_defeated() or self.challengee.is_defeated()

    def has_player(self, player_id: int) -> bool:
        return self.challenger.id == player_id or self.challengee.id == player_id

    def get_winner(self) -> Duelist:
        if self.challenger.is_defeated():
            return self.challengee
        elif self.challengee.is_defeated():
            return self.challenger
        else:
            return None

    def get_random_move(self, moves: List[DuelMove]):
        weights = [move.weight for move in moves]
        selected_move = random.choices(moves, weights, k=1)[0]
        return selected_move
