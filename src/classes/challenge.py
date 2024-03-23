from typing import List


class Challenge:
    """Represents a challenge a player has to complete"""

    def __init__(self, challenger, challengee, message: str):
        self.challenger = challenger
        self.challengee = challengee
        self.message = message
        self.is_complete = False


class ChallengeManager:
    """Tracks challenges and provides helper methods for challenges"""

    def __init__(self):
        self.challenges = []

    def add_challenge(self, challenge: Challenge) -> None:
        """
        Add a challenge to the active challenges.

        Parameters:
        - challenge (Challenge): The challenge to add.
        """
        self.challenges.append(challenge)

    def remove_challenge(self, challenge: Challenge) -> None:
        """
        Remove a challenge from the active challenges.

        Parameters:
        - challenge (Challenge): The challenge to remove.
        """
        self.challenges.remove(challenge)

    def get_player_challenges(self, player_id) -> List[Challenge]:
        """
        Get all the challenges in which a player is being challenged.

        Parameters:
        - player_id (int): The Discord ID of the player.

        Returns:
        - List[Challenge]: All the players challenges.
        """
        return [
            challenge
            for challenge in self.challenges
            if player_id == challenge.challengee
        ]

    def player_has_challenge(self, player_id) -> bool:
        """
        Returns True if the player has an active challenge.

        Parameters:
        - player_id (int): The Discord ID of the player.

        Returns:
        - bool: True if the player has a challenge.
        """
        return any(player_id == challenge.challengee for challenge in self.challenges)

