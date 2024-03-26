import random
import asyncio
from datetime import datetime
import discord
from discord.ext import commands

from classes.horse_race import HorseRace
from schemas.player import Player
from helper import get_embed


class GambleCog(commands.Cog):
    """
    Gathers commands relevant for gambling
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="gamble",
        description="Gamble on a horse race. Optionally add insurance for 15% of the total bet.",
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def gamble(self, ctx: commands.Context, row: int, amount: int, use_insurance: bool = False):
        if not 1 <= row <= 4:
            raise commands.BadArgument("You must gamble on rows 1-4")

        if amount < 1:
            raise commands.BadArgument("Must wager at least 1 coin")

        # Gather player information
        player = self.bot.player_service.get_player(ctx.author.id)
        player_name = ctx.author.name
        player_avatar = player.active_avatar

        if use_insurance:
            insurance_cost = max(1, int(amount * 0.15))
            bet_cost = amount + insurance_cost
        else:
            bet_cost = amount

        if player.get_coins() < bet_cost:
            raise commands.BadArgument("You do not have enough coins")

        player.remove_coins(bet_cost)
        has_horse_steroids = player.has_modifier("horse_steroids")

        horse_race = HorseRace(row - 1, player_avatar, has_horse_steroids)

        embed = get_embed(
            "Horse Race", horse_race.get_race_string(), discord.Color.purple()
        )
        message = await ctx.send(embed=embed)

        for _ in horse_race.simulate_race():
            updated_message = embed.copy()
            updated_message.description = horse_race.get_race_string()
            await message.edit(embed=updated_message)

            embed = updated_message
            await asyncio.sleep(0.1)

        nr_coins_won = horse_race.get_nr_coins_won(amount)

        if use_insurance and nr_coins_won == 0:
            nr_coins_won = amount // 2

        # Fetch player info again to avoid race condition
        player = self.bot.player_service.get_player(ctx.author.id)

        # Save race information
        self.bot.horse_race_service.add_horse_race(
            datetime.today, player.id, amount, nr_coins_won
        )

        player.add_coins(nr_coins_won)

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
            item = self.bot.item_service.get_item("avatar_case")
            player.add_item(item.id)
            await ctx.send(
                content=f"🍀 {ctx.author.mention} got a {item.name} {item.symbol} in a drop! 🍀"
            )
