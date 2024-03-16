import math
import random
import asyncio
from datetime import datetime
from typing import List
import discord
from discord.ext import commands

from schemas.player import Player
from helper import get_embed
from const import EMOJI_ROCKET, EMOJI_BABY, EMOJI_TROLLEY, EMOJI_RABBIT


class GambleCog(commands.Cog):
    """
    Gathers commands relevant for gambling
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="gamble",
        description="Invest your well earned coins in a horse race, kiddo",
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def gamble(
        self, ctx: commands.Context, row: int, amount: int, use_insurance: bool = False
    ):
        if not 1 <= row <= 4:
            raise commands.BadArgument("You must gamble on rows 1-4")

        if amount < 1:
            raise commands.BadArgument("You must gamble at least 1 coin")

        row -= 1  # Correct the index
        player = self.bot.player_service.get_player(ctx.author.id)
        player_name = ctx.author.name
        player_avatar = player.active_avatar

        if use_insurance:
            insurance_cost = max(1, amount // 10)
            self.bot.player_service.remove_coins(player, amount + insurance_cost)
        else:
            self.bot.player_service.remove_coins(player, amount)

        results = await handle_race_message(ctx, row, player_avatar)
        nr_coins_won = get_nr_coins_won(results, row, amount)

        if use_insurance and nr_coins_won == 0:
            nr_coins_won = amount // 2

        # Fetch player info again to avoid race condition
        player = self.bot.player_service.get_player(ctx.author.id)

        # Save race information
        self.bot.horse_race_service.add_horse_race(
            datetime.today, player.id, amount, nr_coins_won
        )

        self.bot.player_service.add_coins(player, nr_coins_won)

        result_embed = get_embed(
            "Horse Race Results",
            f"{player_name} won {nr_coins_won} coin(s)!",
            discord.Color.gold(),
        )
        await ctx.send(embed=result_embed)

        # If player bets at least 10, give chance to drop case
        if amount >= 10:
            await self.handle_case_drop(ctx, player)

    @gamble.error
    async def gamble_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`gamble` error: {error}")

    async def handle_case_drop(self, ctx: commands.Context, player: Player):
        # 10% chance to drop a case
        if random.random() < 0.1:
            item = self.bot.store.get_item("Avatar Case")
            self.bot.player_service.add_item(player, item)
            await ctx.send(content=f"🍀 {ctx.author.mention} got a case in a drop! 🍀")


async def handle_race_message(ctx: commands.Context, row: int, avatar: str):
    # Race variables
    values = [0, 0, 0, 0]
    length = 20
    symbols = [EMOJI_ROCKET, EMOJI_BABY, EMOJI_TROLLEY, EMOJI_RABBIT]

    if avatar:
        symbols[row] = avatar

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


def get_nr_coins_won(standings: List[int], row: int, amount: int) -> int:
    bet_result_index = standings.index(row)
    winnings_table = {0: 2, 1: 1.5, 2: 0.5, 3: 0}
    return math.floor(winnings_table[bet_result_index] * amount)
