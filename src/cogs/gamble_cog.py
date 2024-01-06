import math
import random
import asyncio
from typing import List, Dict, Any
import discord
from discord.ext import commands
from tabulate import tabulate

from schemas.player import Player
from helper import get_embed
from const import (
    EMOJI_ROCKET,
    EMOJI_PENGUIN,
    EMOJI_OCTOPUS,
    EMOJI_SANTA,
    HORSE_INSURANCE_MODIFIER,
    ROULETTE_ICON,
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

    @commands.hybrid_command(
        name="gamble",
        description="Invest your well earned coins in a horse race, kiddo",
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def gamble(self, ctx: commands.Context, row: int, amount: int):
        if not 1 <= row <= 4:
            raise commands.BadArgument("You must gamble on rows 1-4")

        if amount < 1:
            raise commands.BadArgument("You must gamble at least 1 coin")

        row -= 1  # Correct the index

        player = self.bot.player_service.get_player(ctx.author.id)
        player_name = ctx.author.name

        self.bot.player_service.remove_coins(player, amount)

        results = await handle_race_message(player, row, ctx)
        nr_coins_won = get_gamble_result(results, row, amount)

        if HORSE_INSURANCE_MODIFIER in player.modifiers and nr_coins_won == 0:
            self.bot.player_service.use_modifier(player, HORSE_INSURANCE_MODIFIER)
            nr_coins_won = amount // 2

        self.bot.player_service.add_coins(player, nr_coins_won)

        result_embed = get_embed(
            "Horse Race Results",
            f"{player_name} won {nr_coins_won} coin(s)!",
            discord.Color.gold(),
        )
        await ctx.send(embed=result_embed)

    @gamble.error
    async def gamble_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`gamble` error: {error}")

    @commands.hybrid_command(name="roulette", description="Welcome to Vegas!")
    async def roulette(self, ctx: commands.Context, amount: int):
        player = self.bot.player_service.get_player(ctx.author.id)

        self.bot.player_service.remove_coins(player, amount)

        if player.id in self.roulette_event.participants:
            self.roulette_event.participants[player.id]["coins"] += amount
        else:
            self.roulette_event.participants[player.id] = {}
            self.roulette_event.participants[player.id]["user"] = ctx.author
            self.roulette_event.participants[player.id]["coins"] = amount

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
            embed.set_thumbnail(url=ROULETTE_ICON)
            await ctx.send(embed=embed)

            countdown_length = min(event_time, 10)
            await asyncio.sleep(event_time - countdown_length)
            await handle_roulette_countdown(countdown_length, ctx)
            await self.handle_roulette_event_end(ctx)

            self.roulette_event.participants = {}
            self.roulette_event.event_started = False
            return

        total_players = len(self.roulette_event.participants)
        total_coins = sum(
            player["coins"] for player in self.roulette_event.participants.values()
        )

        odds_table = get_odds_table(self.roulette_event.participants)

        embed = get_embed(
            f"Roulette Event Joined by {ctx.author.name}",
            (
                f"🎲 {ctx.author.name} has joined the roulette with {amount} coin(s)!\n\n"
                f"👥 **Total Players:** {total_players}\n"
                f"💰 **Total coins:** {total_coins}\n\n"
            ),
            discord.Color.blue(),
        )
        embed.add_field(name="📊 Odds", value=f"```{odds_table}```", inline=False)
        await ctx.send(embed=embed)

    @roulette.error
    async def roulette_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`roulette` error: {error}")

    async def handle_roulette_event_end(self, ctx: commands.Context):
        participants = self.roulette_event.participants

        if len(participants) < 2:
            # Refund player coins
            for player_id in participants:
                player = self.bot.player_service.get_player(player_id)
                self.bot.player_service.add_coins(
                    player, participants[player_id]["coins"]
                )

            await ctx.send(
                content="Not enough participants for roulette to start. Refunding coins."
            )
            return

        users = [user_info["user"] for user_info in participants.values()]
        user_coins = [user_info["coins"] for user_info in participants.values()]

        winner = random.choices(users, weights=user_coins, k=1)[0]
        winner_player = self.bot.player_service.get_player(winner.id)
        win_amount = sum(user_coins)

        odds_table = get_odds_table(participants)

        self.bot.player_service.add_coins(winner_player, win_amount)

        embed = get_embed(
            "🎉 Roulette Winner Announcement 🎉",
            f"Congratulations {winner.mention}!",
            discord.Color.gold(),
        )
        embed.add_field(
            name=f"{winner.name} won!",
            value=f"You win {win_amount} coin(s).",
            inline=False,
        )
        embed.add_field(
            name="📊 Odds",
            value=f"```{odds_table}```",
            inline=False,
        )
        await ctx.send(embed=embed)


async def handle_roulette_countdown(seconds: int, ctx: commands.Context):
    message = await ctx.send(f"Roulette ending in {seconds} seconds")

    while seconds > 0:
        await asyncio.sleep(1)
        seconds -= 1
        await message.edit(content=f"Roulette ending in {seconds} seconds")


def get_odds_table(participants: Dict[int, Any]) -> str:
    table_data = []
    total_coins = sum(player["coins"] for player in participants.values())

    for user_info in participants.values():
        odds = (user_info["coins"] / total_coins) * 100
        line = [user_info["user"].name, user_info["coins"], f"{odds:.2f}%"]
        table_data.append(line)

    table_str = tabulate(
        table_data, headers=["Player", "Coins", "Odds"], tablefmt="plain"
    )
    return table_str


async def handle_race_message(player: Player, row: int, ctx: commands.Context):
    # Race variables
    values = [0, 0, 0, 0]
    length = 20
    symbols = [EMOJI_ROCKET, EMOJI_PENGUIN, EMOJI_OCTOPUS, EMOJI_SANTA]

    if player.active_avatar:
        symbols[row] = player.active_avatar.icon

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
