import json
import math
import random
import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import BadArgument, Context, CommandError
from typing import Dict, List

from helper import get_embed
from const import LOCK_MODIFIER, NINJA_LESSON_MODIFIER, SIGNAL_JAMMER_MODIFIER


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
        self.challenges.append(challenge)

    def remove_challenge(self, challenge: Challenge) -> None:
        self.challenges.remove(challenge)

    def get_player_challenge(self, player_id) -> Challenge:
        for challenge in self.challenges:
            if player_id == challenge.challengee:
                return challenge
        return None

    def player_has_challenge(self, player_id) -> bool:
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

        if self.challenge_manager.player_has_challenge(player.id):
            raise commands.BadArgument(
                "You cannot steal from more than one player at the same time"
            )

        if LOCK_MODIFIER in target_player.modifiers:
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
            nr_ninja_modifiers = player.modifiers.count(NINJA_LESSON_MODIFIER)
            if not weighted_chance(
                player.coins, target_player.coins, nr_ninja_modifiers
            ):
                await self.handle_steal_fail(
                    ctx, player.id, "You did not succeed in stealing"
                )
                return

            # Construct challenge to send to other player
            nouns = self.words["nouns"]
            verbs = self.words["verbs"]
            adverbs = self.words["adverbs"]
            adjectives = self.words["adjectives"]
            prepositional_phrases = self.words["prepositional_phrases"]
            direct_objects = self.words["direct_objects"]
            use_hard_words = SIGNAL_JAMMER_MODIFIER in player.modifiers

            message = generate_message(
                nouns,
                verbs,
                adverbs,
                adjectives,
                prepositional_phrases,
                direct_objects,
                use_hard_words,
            )

            # Insert non-breaking space to prevent copy-pasting
            modified_message = insert_nbsp(message)

            steal_embed = get_embed(
                f"{ctx.author.name} is stealing from {user.name}!",
                f"{user.mention}, type the following sentence in the next 30 seconds to prevent them from stealing!",
                0xFFA600,
            )
            steal_embed.add_field(
                name="Type:", value=f"```{modified_message}```", inline=False
            )

            await ctx.send(embed=steal_embed)

            challenge = Challenge(player.id, target_player.id, message)
            self.challenge_manager.add_challenge(challenge)

            await asyncio.sleep(30)

            if challenge.is_complete:
                await ctx.send(
                    content=f"{user.name} managed to get away with all their coins!"
                )
            else:
                # Get player objects again to prevent race condition
                player = self.bot.player_service.get_player(ctx.author.id)
                target_player = self.bot.player_service.get_player(user.id)

                coins_stolen = int(random.random() * target_player.coins / 2)
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

        challenge = self.challenge_manager.get_player_challenge(message.author.id)

        if challenge.message == message.content:
            challenge.is_complete = True

    async def handle_steal_fail(self, ctx: Context, player_id, message):
        """Remove random amount of coins from player who tried to steal"""
        # Get player again to prevent any race conditions
        player = self.bot.player_service.get_player(ctx.author.id)

        coins_lost = int(random.random() * player.coins / 4)
        self.bot.player_service.remove_coins(player, coins_lost)
        await ctx.send(content=f"{message}. You lost {coins_lost} coins.")


def generate_message(
    nouns,
    verbs,
    adverbs,
    adjectives,
    prepositional_phrases,
    direct_objects,
    use_hard_words: bool = False,
):
    threshold = 10

    # Filter out short words if use_hard_words is False
    if not use_hard_words:
        filtered_nouns = [noun for noun in nouns if len(noun) <= threshold]
        nouns = filtered_nouns if filtered_nouns else nouns

        filtered_verbs = [verb for verb in verbs if len(verb) <= threshold]
        verbs = filtered_verbs if filtered_verbs else verbs

        filtered_adverbs = [adverb for adverb in adverbs if len(adverb) <= threshold]
        adverbs = filtered_adverbs if filtered_adverbs else adverbs

        filtered_adjectives = [
            adjective for adjective in adjectives if len(adjective) <= threshold
        ]
        adjectives = filtered_adjectives if filtered_adjectives else adjectives

        filtered_prepositional_phrases = [
            phrase for phrase in prepositional_phrases if len(phrase) <= threshold
        ]
        prepositional_phrases = (
            filtered_prepositional_phrases
            if filtered_prepositional_phrases
            else prepositional_phrases
        )

        filtered_direct_objects = [do for do in direct_objects if len(do) <= threshold]
        direct_objects = (
            filtered_direct_objects if filtered_direct_objects else direct_objects
        )

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


def insert_nbsp(message: str):
    nbsp = "\u200b"
    return nbsp.join(message)


def weighted_chance(a, b, nr_modifiers=0):
    ratio = max(a, b) / min(a, b) if min(a, b) > 0 else max(a, b)

    base_value = 0.5
    decay_rate = 0.075
    base_modifier = 1.05

    probability = base_value * math.exp(-decay_rate * (ratio - 1))

    if nr_modifiers > 0:
        modifier_rate = math.pow(base_modifier, nr_modifiers)
        probability *= modifier_rate

    min_probability = 0.05
    adjusted_probability = max(probability, min_probability)

    return random.random() < adjusted_probability


class StealError(CommandError):
    """Exception raised when interacting with the store"""
