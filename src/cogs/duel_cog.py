import asyncio
import discord
from discord.ext import commands

from classes.duel import Duel, Duelist, DuelState
from helper import get_embed
from schemas.player import Player


class DuelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.duels = []

    @commands.hybrid_group(name="duel", description="Group of duel commands")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def duel(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("No subcommand invoked")

    @duel.error
    async def duel_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"`duel` error: {error}")

    @duel.command(name="start")
    async def duel_start(self, ctx: commands.Context, user: discord.User, amount: int):
        if ctx.author.id == user.id:
            raise commands.BadArgument("Can't duel yourself")

        if amount < 1:
            raise commands.BadArgument("Must wager at least 1 coin")

        for duel in self.duels:
            if duel.has_player(user.id) and duel.state != DuelState.COMPLETED:
                raise commands.BadArgument(
                    "You have an active challenge with this user"
                )

        p1 = self.bot.player_service.get_player(ctx.author.id)
        p2 = self.bot.player_service.get_player(user.id)

        if p2.get_coins() < amount:
            raise commands.BadArgument(
                f"{user.name} doesn't have enough coins for this duel"
            )

        p1.remove_coins(amount)

        challenger = Duelist(ctx.author.name, ctx.author.id, p1.active_avatar)
        challengee = Duelist(user.name, user.id, p2.active_avatar)
        duel = Duel(challenger, challengee, amount)
        self.duels.append(duel)

        embed = get_embed(
            "\U0001F4A5 Duel Request \U0001F4A5",
            f"{ctx.author.name} challenged {user.mention} to a duel for {amount} coins!",
            discord.Color.red(),
        )
        embed.add_field(name="Information", value="Ending in 1 minute", inline=False)
        await ctx.send(embed=embed)

        await asyncio.sleep(60)

        # Duel never got accepted
        if duel.state == DuelState.PENDING:
            # Prevent race condition on player object
            p1 = self.bot.player_service.get_player(ctx.author.id)
            p1.add_coins(amount)

            self.duels.remove(duel)
            await ctx.send(content="Duel request expired, refunded coins")

    @duel_start.error
    async def duel_start_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"`duel start` error: {error}")

    @duel.command(name="accept")
    async def duel_accept(self, ctx: commands.Context, user: discord.User = None):
        if user and ctx.author.id == user.id:
            raise commands.BadArgument("Can't accept a duel from yourself")

        player = self.bot.player_service.get_player(ctx.author.id)

        pending_duels = []

        for duel in self.duels:
            if duel.has_player(ctx.author.id) and duel.state == DuelState.PENDING:
                pending_duels.append(duel)

        if not pending_duels:
            raise commands.BadArgument("No pending duels")

        if user:
            for duel in pending_duels:
                if duel.has_player(user.id):
                    await self.handle_accept_duel(player, ctx, duel)
        else:
            if len(pending_duels) > 1:
                raise commands.BadArgument("You have more than one pending duel")

            duel = pending_duels.pop()
            await self.handle_accept_duel(player, ctx, duel)

    @duel_accept.error
    async def duel_accept_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"`duel accept` error: {error}")

    async def handle_accept_duel(
        self, player: Player, ctx: commands.Context, duel: Duel
    ):
        self.bot.player_service.remove_coins(player, duel.wager)
        duel.accept()
        await self.simulate_duel(ctx, duel)

    async def simulate_duel(self, ctx: commands.Command, duel: Duel):
        embed = get_embed(
            f"Duel: {duel.challenger.name} vs. {duel.challengee.name}",
            f"```{duel.generate_initial_message()}```",
            discord.Color.red(),
        )
        message = await ctx.send(embed=embed)

        await asyncio.sleep(3)

        for duel_string in duel.simulate():
            embed.description = f"```{duel_string}```"
            await message.edit(embed=embed)
            await asyncio.sleep(3)

        winner = duel.get_winner()

        # Prevent race condition
        player = self.bot.player_service.get_player(winner.id)
        player.add_coins(duel.wager * 2)

        embed.description = f"{winner.name} won {duel.wager} coin(s)!"
        await ctx.send(embed=embed)
