import math
import random
import asyncio
from typing import List
import discord
from discord.ext import commands

from helper import get_embed
from const import (
    EMOJI_ROCKET,
    EMOJI_PENGUIN,
    EMOJI_OCTOPUS,
    EMOJI_SANTA,
)


class GambleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def gamble(self, ctx: commands.Context, row: int, amount: int):
        if not 1 <= row <= 4:
            raise commands.BadArgument("You must gamble on rows 1-4")

        if amount < 1:
            raise commands.BadArgument("You must gamble at least 1 token")

        author_id = ctx.author.id
        author_name = ctx.author.name
        author_tokens = self.bot.token_manager.get_tokens(author_id)

        if author_tokens < amount:
            raise commands.CommandError("Insufficient tokens")

        self.bot.token_manager.update_tokens(author_id, -amount)

        results = await handle_race_message(ctx)

        nr_tokens_won = get_gamble_result(results, row - 1, amount)
        self.bot.token_manager.update_tokens(author_id, nr_tokens_won)

        result_embed = get_embed(
            "Horse Race Results",
            f"{author_name} won {nr_tokens_won} token(s)!",
            discord.Color.gold(),
        )
        await ctx.send(embed=result_embed)

    @gamble.error
    async def gamble_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content="`!gamble` error: Incorrect arguments")
        elif isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!gamble` error: {error}")


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
        raise Exception("Values and symbols must have the same length")

    if max(cur_values) > race_length:
        raise Exception("Values must be less than or equal to goal")

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
