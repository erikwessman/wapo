import json
import random
from typing import Dict, Any


class CaseAPI:
    """"""

    def __init__(self, file_path: str):
        case_data = self._load_case_data(file_path)
        self._items = case_data["items"]
        self._odds_base = case_data["odds_base"]
        self._odds_improved = case_data["odds_improved"]

    def _load_case_data(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise ValueError(f"The file '{file_path}' was not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Could not decode the contents of {file_path}")

    def get_random_case_item(self, improved_odds: bool = True):
        odds = self._odds_improved if improved_odds else self._odds_base
        odds_list = [(tier, odds[tier]) for tier in odds]

        total_odds = sum(odd[1] for odd in odds_list)
        normalized_odds = [odd[1] / total_odds for odd in odds_list]

        chosen_tier = random.choices([tier[0] for tier in odds_list], weights=normalized_odds, k=1)[0]
        chosen_item = random.choice(self._items[chosen_tier])

        return chosen_tier, chosen_item

    def get_tiers(self, improved_odds: bool = True):
        """Get a dict of the case tiers and items"""
        odds = self._odds_improved if improved_odds else self._odds_base

        tier_dict = {}

        for tier, drop_rate in odds.items():
            items = self._items[tier]
            tier_dict[tier] = {
                "items": items,
                "drop_rate": drop_rate
            }

        return tier_dict
