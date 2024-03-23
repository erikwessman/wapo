import random
import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from typing import Any, Dict
from tabulate import tabulate

from helper import get_embed
from const import ROULETTE_ICON


class RouletteEvent:
    """
    Helper class for keeping track of events
    """

    def __init__(self):
        self.participants = {}
        self.event_started = False


class RouletteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roulette_event = RouletteEvent()

    @commands.hybrid_command(name="roulette", description="Welcome to Vegas!")
    async def roulette(self, ctx: commands.Context, amount: int):
        player = self.bot.player_service.get_player(ctx.author.id)

        if player.get_coins() > amount:
            raise commands.BadArgument("Not enough coins")

        player.remove_coins(amount)

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
                f"Started by {ctx.author.name} with {amount} coin(s)",
                discord.Color.red(),
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
        total_coins = sum(player["coins"] for player in self.roulette_event.participants.values())

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
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`roulette` error: {error}")

    async def handle_roulette_event_end(self, ctx: commands.Context):
        participants = self.roulette_event.participants

        if len(participants) < 2:
            for player_id in participants:
                player = self.bot.player_service.get_player(player_id)
                player.add_coins(participants[player_id]["coins"])

            await ctx.send(content="Not enough participants for roulette to start. Refunding coins.")
            return

        users = [user_info["user"] for user_info in participants.values()]
        user_coins = [user_info["coins"] for user_info in participants.values()]

        winner = random.choices(users, weights=user_coins, k=1)[0]
        winner_player = self.bot.player_service.get_player(winner.id)
        win_amount = sum(user_coins)

        winner_player.add_coins(win_amount)

        odds_table = get_odds_table(participants)
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

        # Save roulette information
        player_dict = {str(player_id): data["coins"] for player_id, data in participants.items() }
        self.bot.roulette_service.add_roulette(datetime.today(), player_dict, winner.id)


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
