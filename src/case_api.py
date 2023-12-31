import json
import random
from typing import Dict, Any
from discord.ext.commands import CommandError


class CaseAPI:
    """"""

    def __init__(self, file_path: str):
        self._cases = self._load_cases(file_path)

    def _load_cases(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise CaseAPIError(f"The file '{file_path}' was not found.")
        except json.JSONDecodeError:
            raise CaseAPIError(f"Could not decode the contents of {file_path}")

    def get_case_item(self):
        tier_names = []
        tier_probabilities = []

        for tier, info in self._cases.items():
            tier_names.append(tier)
            tier_probabilities.append(info["drop_rate"])

        total = sum(tier_probabilities)
        tier_probabilities = [x / total for x in tier_probabilities]

        selected_tier = random.choices(tier_names, weights=tier_probabilities, k=1)[0]

        return selected_tier, random.choice(self._cases[selected_tier]["items"])

    def get_tiers(self):
        """Get a dict of the case tiers and items"""
        return self._cases.copy()


class CaseAPIError(CommandError):
    """Exception raised when interacting with the case API"""
