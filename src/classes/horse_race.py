import random
import math
from typing import List

from const import GAMBLE_EMOJIS


class HorseRace:
    def __init__(self, bet_amount: int, row: int, avatar: str, length=20):
        self.values = [0, 0, 0, 0]
        self.length = length
        self.bet_amount = bet_amount
        self.symbols = GAMBLE_EMOJIS.copy()
        if avatar:
            self.symbols[row] = avatar
        self.standings = []

    def simulate_race(self):
        below_threshold = set(range(len(self.values)))
        while below_threshold:
            index = random.choice(list(below_threshold))
            self.values[index] += 1

            if self.values[index] >= self.length:
                below_threshold.remove(index)
                self.standings.append(index)

            yield self.values, self.standings

    def get_race_string(self):
        lines = []
        lines.append("```")
        for i, line_prog in enumerate(self.values):
            line = ""
            line += "#" * line_prog
            line += self.symbols[i]
            line += "." * (self.length - line_prog)
            lines.append(line)
        lines.append("```")

        for i, standing in enumerate(self.standings):
            lines[standing + 1] += f"({i+1})"

        return "\n\n".join(lines)

    def get_results(self):
        pass

    def get_nr_coins_won(self, standings: List[int], row: int, amount: int) -> int:
        bet_result_index = standings.index(row)
        winnings_table = {0: 2, 1: 1.5, 2: 0.5, 3: 0}
        return math.floor(winnings_table[bet_result_index] * amount)
