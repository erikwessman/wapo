import math
import random
import asyncio
import datetime
from typing import List
import discord
from discord.ext import commands

from helper import get_embed
from const import (
    EMOJI_ROCKET,
    EMOJI_PENGUIN,
    EMOJI_OCTOPUS,
    EMOJI_SANTA,
    HORSIE_STEROIDS_MODIFIER_NAME,
)


class Event:
    """
    Helper class for keeping track of events
    """

    def __init__(self):
        self.participants = {}
        self.event_started = False


class GambleCog(commands.Cog):
    """
    Gathers commands relevant for gambling
    """

    def __init__(self, bot):
        self.bot = bot
        self.roulette_event = Event()

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def gamble(self, ctx: commands.Context, row: int, amount: int):
        if not 1 <= row <= 4:
            raise commands.BadArgument("You must gamble on rows 1-4")

        if amount < 1:
            raise commands.BadArgument("You must gamble at least 1 token")

        player = self.bot.player_service.get_player(ctx.author.id)
        player_name = ctx.author.name

        if player.tokens < amount:
            raise commands.CommandError("Insufficient tokens")

        self.bot.player_service.update_tokens(player.id, -amount)

        results = await handle_race_message(ctx)
        nr_tokens_won = get_gamble_result(results, row - 1, amount)

        if player.has_modifier(HORSIE_STEROIDS_MODIFIER_NAME):
            self.bot.player_service.use_modifier(
                player.id, HORSIE_STEROIDS_MODIFIER_NAME
            )
            nr_tokens_won *= 2

        self.bot.player_service.update_tokens(player.id, nr_tokens_won)

        result_embed = get_embed(
            "Horse Race Results",
            f"{player_name} won {nr_tokens_won} token(s)!",
            discord.Color.gold(),
        )
        await ctx.send(embed=result_embed)

    @gamble.error
    async def gamble_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content="`!gamble` error: Incorrect arguments")
        elif isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!gamble` error: {error}")

    @commands.command()
    async def roulette(self, ctx: commands.Context, amount: int):
        player = self.bot.player_service.get_player(ctx.author.id)

        if player.tokens < amount:
            raise commands.CommandError("Insufficient tokens")

        self.bot.player_service.update_tokens(player.id, -amount)

        if player.id in self.roulette_event.participants:
            self.roulette_event.participants[player.id]["tokens"] += amount
        else:
            self.roulette_event.participants[player.id] = {}
            self.roulette_event.participants[player.id]["user"] = ctx.author
            self.roulette_event.participants[player.id]["tokens"] = amount

        if not self.roulette_event.event_started:
            self.roulette_event.event_started = True
            event_time = 5 * 60

            embed = get_embed(
                "🌟 Roulette Event Alert! 🌟",
                f"Started by {ctx.author.name}",
                discord.Color.blue(),
            )
            embed.add_field(
                name="Information",
                value=f"Ending in {event_time // 60} minutes",
                inline=False,
            )
            embed.set_thumbnail(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Roulette-finlandsfarja.jpg/1280px-Roulette-finlandsfarja.jpg"
            )
            await ctx.send(embed=embed)

            await asyncio.sleep(event_time)
            await self.handle_roulette_event_end(ctx)

            self.roulette_event.participants = {}
            self.roulette_event.event_started = False
            return

        total_players = len(self.roulette_event.participants)
        total_tokens = sum(
            player["tokens"] for player in self.roulette_event.participants.values()
        )

        await ctx.send(
            (
                f"{ctx.author.name} has joined the roulette with {amount}\n"
                f"{total_players} player(s) total\n"
                f"{total_tokens} token(s) total\n"
            )
        )

    @roulette.error
    async def roulette_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!roulette error`: {error}")

    async def handle_roulette_event_end(self, ctx: commands.Context):
        participants = self.roulette_event.participants

        if len(participants) < 2:
            await ctx.send(content="Not enough participants for roulette")
            return

        users = [user_info["user"] for user_info in participants.values()]
        user_tokens = [user_info["tokens"] for user_info in participants.values()]

        winner = random.choices(users, weights=user_tokens, k=1)[0]
        win_amount = sum(user_tokens)

        self.bot.player_service.update_tokens(winner.id, win_amount)

        embed = get_embed(
            "🎉 Roulette Winner Announcement 🎉",
            f"Congratulations {winner.mention}!",
            discord.Color.gold(),
        )
        embed.add_field(
            name=f"{winner.name} won!",
            value=f"You win {win_amount} token(s).",
            inline=False,
        )
        await ctx.send(embed=embed)


async def handle_race_message(ctx: commands.Context):
    # Race variables
    values = [0, 0, 0, 0]
    length = 20
    symbols = [EMOJI_ROCKET, EMOJI_PENGUIN, EMOJI_OCTOPUS, EMOJI_SANTA]

    embed = get_embed(
        "Horse Race",
        get_race_string(values, [], symbols, length),
        discord.Color.purple(),
    )
    message = await ctx.send(embed=embed)

    for cur_values, cur_standings in simulate_race(values, length):
        updated_message = embed.copy()
        updated_message.description = get_race_string(
            cur_values, cur_standings, symbols, length
        )
        await message.edit(embed=updated_message)

        embed = updated_message
        await asyncio.sleep(0.1)

    return cur_standings


def simulate_race(values: List[int], length: int):
    standings = []
    below_threshold = set(range(len(values)))

    # Increment a random element until every horse has reached the goal
    while below_threshold:
        index = random.choice(list(below_threshold))
        values[index] += 1

        if values[index] >= length:
            below_threshold.remove(index)
            standings.append(index)

        yield values, standings


def get_race_string(
    cur_values: List[int],
    cur_standings: List[int],
    symbols: List[str],
    race_length: int,
) -> str:
    if len(cur_values) != len(symbols):
        raise ValueError("Values and symbols must have the same length")

    if max(cur_values) > race_length:
        raise ValueError("Values must be less than or equal to goal")

    lines = []
    lines.append("```")
    for i, line_prog in enumerate(cur_values):
        line = ""
        line += "#" * line_prog
        line += symbols[i]
        line += "." * (race_length - line_prog)
        lines.append(line)
    lines.append("```")

    for i, standing in enumerate(cur_standings):
        # Add 1 to standing to compensate for the ```
        lines[standing + 1] += f"({i+1})"

    return "\n\n".join(lines)


def get_gamble_result(standings: List[int], row: int, amount: int) -> int:
    bet_result_index = standings.index(row)
    winnings_table = {0: 2, 1: 1.5, 2: 0.5, 3: 0}
    return math.floor(winnings_table[bet_result_index] * amount)
