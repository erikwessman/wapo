import json
import math
import random
import discord
import asyncio
import numpy as np
from discord.ext import commands
from discord.ext.commands import BadArgument, Context, CommandError
from typing import Dict, List

from helper import get_embed
from const import (
    LOCK_MODIFIER,
    NINJA_LESSON_MODIFIER,
    SIGNAL_JAMMER_MODIFIER,
    EMOJI_MONEY_WITH_WINGS,
)


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
        return [challenge for challenge in self.challenges if player_id == challenge.challengee]

    def player_has_challenge(self, player_id) -> bool:
        """
        Returns True if the player has an active challenge.

        Parameters:
        - player_id (int): The Discord ID of the player.

        Returns:
        - bool: True if the player has a challenge.
        """
        return any(player_id == challenge.challengee for challenge in self.challenges)


class StealCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.words = self._load_words("data/words.json")
        self.challenge_manager = ChallengeManager()

    def _load_words(self, file_path: str) -> Dict[str, List[str]]:
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise StealError(f"The file '{file_path}' was not found.")
        except json.JSONDecodeError:
            raise StealError(f"Could not decode the contents of '{file_path}'")

    @commands.hybrid_command(name="steal", description="Steal coins from a user")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def steal(self, ctx: commands.Context, user: discord.User):
        player = self.bot.player_service.get_player(ctx.author.id)
        target_player = self.bot.player_service.get_player(user.id)

        if player.id == target_player.id:
            raise commands.BadArgument("You cannot steal from yourself")

        if target_player.id == self.bot.user.id:
            raise commands.BadArgument("You cannot steal from me!")

        if self.bot.player_service.has_modifier(target_player, LOCK_MODIFIER):
            # Lock gets used, remove it
            self.bot.player_service.use_modifier(target_player, LOCK_MODIFIER)
            await self.handle_steal_fail(
                ctx,
                player.id,
                "The other player had a lock that prevented you from stealing",
            )
            return
        else:
            # Make stealing harder, especially from the rich
            # But increase the odds for each ninja lesson modifier
            nr_ninja_modifiers = player.modifiers.get(NINJA_LESSON_MODIFIER, 0)
            if not weighted_chance(
                player.coins, target_player.coins, nr_ninja_modifiers
            ):
                await self.handle_steal_fail(
                    ctx, player.id, "You did not succeed in stealing"
                )
                return

            use_hard_words = self.bot.player_service.has_modifier(player, SIGNAL_JAMMER_MODIFIER)
            prepared_words = prepare_words(self.words, use_hard_words)
            message = generate_message(**prepared_words)

            # Prevent copy-pasting
            modified_message = insert_nbsp(message)

            steal_embed = get_embed(
                f"{EMOJI_MONEY_WITH_WINGS} {ctx.author.name} is stealing from {user.name}! {EMOJI_MONEY_WITH_WINGS}",
                f"{user.mention}, type the following sentence in the next 45 seconds to prevent them from stealing!",
                0xFFA600,
            )
            steal_embed.add_field(
                name="Type:", value=f"```{modified_message}```", inline=False
            )

            await ctx.send(embed=steal_embed)

            challenge = Challenge(player.id, target_player.id, message)
            self.challenge_manager.add_challenge(challenge)

            await asyncio.sleep(45)

            if not challenge.is_complete:
                # Get player objects again to prevent race condition
                player = self.bot.player_service.get_player(ctx.author.id)
                target_player = self.bot.player_service.get_player(user.id)

                coins_stolen = get_norm(target_player.coins, 30, 25)
                self.bot.player_service.add_coins(player, coins_stolen)
                self.bot.player_service.remove_coins(target_player, coins_stolen)
                await ctx.send(
                    content=f"{ctx.author.name} stole {coins_stolen} coins from {user.name}!"
                )

            self.challenge_manager.remove_challenge(challenge)

    @steal.error
    async def steal_error(self, ctx: Context, error):
        if isinstance(error, BadArgument):
            await ctx.send(content=f"`steal` error: {error}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.challenge_manager.player_has_challenge(message.author.id):
            return

        challenges = self.challenge_manager.get_player_challenges(message.author.id)

        for challenge in challenges:
            if challenge.message == message.content:
                challenge.is_complete = True
                await message.channel.send(
                    content=f"{message.author.name} managed to get away with all their coins!"
                )

    async def handle_steal_fail(
        self, ctx: Context, player_id: int, message: str
    ) -> None:
        """
        Handles the case when a player fails to steal from another player.
        Removes a random amount of coins from the player and sends a message.

        Parameters:
        - ctx (discord.Context): Message context.
        - player_id (int): ID of the player that attempted to steal.
        - message (str): Message to send.
        """
        # Get player again to prevent any race conditions
        player = self.bot.player_service.get_player(player_id)

        coins_lost = get_norm(player.coins, 20, 15)
        self.bot.player_service.remove_coins(player, coins_lost)
        await ctx.send(content=f"{message}. You lost {coins_lost} coins.")


def prepare_words(word_dict: Dict[str, Dict[str, List[str]]], use_hard=False) -> Dict[str, List[str]]:
    """
    Prepares and returns a dictionary of words to be used in generate_message, combining easy and hard words based on use_hard flag.

    Parameters:
    - word_dict (Dict[str, Dict[str, List[str]]]): Word dictionary.
    - use_hard (bool): Include hard words in the output.

    Returns:
    - Dict[str, List[str]]: List of words.
    """
    prepared_words = {}
    for category, lists in word_dict.items():
        prepared_words[category] = lists['easy'][:]
        if use_hard:
            prepared_words[category] += lists['hard']
    return prepared_words


def generate_message(
    nouns: List[str],
    verbs: List[str],
    adverbs: List[str],
    adjectives: List[str],
    prepositional_phrases: List[str],
    direct_objects: List[str],
) -> str:
    """
    Generates a random message based on categories of words.

    Parameters:
    - nouns (List[str]): List of nouns.
    - verbs (List[str]): List of verbs.
    - adverbs (List[str]): List of adverbs.
    - adjectives (List[str]): List of adjectives.
    - prepositional_phrases (List[str]): List of prepositional phrases.
    - direct_objects (List[str]): List of direct objects.

    Returns:
    - str: Generated message.
    """
    noun = random.choice(nouns)
    verb = random.choice(verbs)
    optional_modifiers = (
        adverbs
        + prepositional_phrases
        + [f"{adj} {do}" for adj, do in zip(adjectives, direct_objects)]
    )
    modifier = random.choice([None] + optional_modifiers)

    if modifier in adjectives:
        message = f"{modifier} {noun} {verb}"
    elif modifier:
        message = f"{noun} {verb} {modifier}"
    else:
        message = f"{noun} {verb}"

    return message


def insert_nbsp(message: str) -> str:
    """
    Inserts a non-breaking-space between every character in the input message.

    Parameters:
    - message (str): Message to modify.

    Returns:
    - str: Modified message.
    """
    nbsp = "\u200b"
    return nbsp.join(message)


def weighted_chance(a: int, b: int, nr_modifiers: int = 0) -> bool:
    """
    Flips a weighted coin and returns True or False.
    The odds are 50/50 when A and B are equal but fall off exponentially as the difference between A and B grows.
    Takes an optional argument nr_modifiers to increase the chance of success.

    Parameters:
    - a (int): Input A.
    - b (int): Input B.
    - nr_modifiers (int, optional): The number of modifiers to increase the odds.

    Returns:
    - bool: Whether the coin flip succeeded or not.
    """
    ratio = max(a, b) / min(a, b) if min(a, b) > 0 else max(a, b)

    base_value = 0.5
    decay_rate = 0.05
    modifier_effect = 0.03

    probability = base_value * math.exp(-decay_rate * (ratio - 1))

    for i in range(nr_modifiers):
        probability += modifier_effect

    min_probability = 0.05
    max_probability = 0.95
    adjusted_probability = min(max(probability, min_probability), max_probability)

    return random.random() < adjusted_probability


def get_norm(value: int, mean: int = 50, std: int = 15) -> int:
    """
    Samples a random integer value between 0 and the input based on a Gaussian distribution.

    Parameters:
    - value (int): The max value to draw from.
    - mean (int, optional): The mean of the Gaussian distribution.
    - std (int, optional): The standard deviation of the Gaussian distribution.

    Returns:
    - int: A random value from the Gaussian distribution.
    """
    norm = np.random.normal(mean, std)
    norm_clamped = max(min(norm, 100), 0)
    output_value = value * (norm_clamped / 100)
    return round(output_value)


class StealError(CommandError):
    """Exception raised when initializing the StealCog"""
