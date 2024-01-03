import discord
from discord.ext import commands

from classes.item import Item
from classes.player import Player
from helper import get_embed
from const import HORSE_INSURANCE_MODIFIER


class PlayerCog(commands.Cog):
    """
    Gathers commands relevant for players
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def profile(self, ctx: commands.Context):
        player_name = ctx.author.name
        player = self.bot.player_service.get_player(ctx.author.id)
        player_inventory = player.inventory
        player_coins = player.coins

        embed = get_embed(
            f"Profile: {player_name}",
            f"Player ID: {player.id}",
            discord.Color.green(),
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(
            name="Inventory",
            value=f"{str(len(player_inventory))} item(s)",
            inline=False,
        )
        embed.add_field(name="Coins", value=str(player_coins), inline=True)

        await ctx.send(embed=embed)

    @profile.error
    async def profile_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!profile` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def coins(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        await ctx.send(content=f"You have {player.coins} coins")

    @coins.error
    async def coins_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!coins` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def holdings(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)

        embed = get_embed("Player Holdings", "", discord.Color.blue())

        for ticker, holding in player.holdings.items():
            embed.add_field(
                name=f"${holding.ticker}",
                value=f"Shares: {holding.shares}\n"
                      f"Average Price: ${holding.average_price:.2f}",
                inline=False
            )

        await ctx.send(embed=embed)

    @coins.error
    async def holdings_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!holdings` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def inventory(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        player_inventory = player.inventory

        embed = get_embed(f"{ctx.author.name}'s Inventory", "", discord.Color.orange())
        embed.set_thumbnail(url=ctx.author.avatar.url)

        if player_inventory:
            for item_id, quantity in player_inventory.items():
                item = self.bot.store.get_item(item_id)
                embed.add_field(
                    name=f"{item.name} {item.symbol} (x{quantity})",
                    value=f"ID: {item.id}",
                    inline=False,
                )
        else:
            embed.add_field(
                name="No items", value="You have no items in your inventory."
            )

        await ctx.send(embed=embed)

    @inventory.error
    async def inventory_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!inventory` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def use(self, ctx: commands.Context, item_id: str):
        player = self.bot.player_service.get_player(ctx.author.id)

        if item_id not in player.inventory:
            raise commands.CommandError("You don't have this item in your inventory")

        item = self.bot.store.get_item(item_id)

        if self.use_item(player, item):
            await ctx.send(content=f"Used {item.name}")
        else:
            raise commands.CommandError("Failed to use item")

    @use.error
    async def use_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!use` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def give(self, ctx, user: discord.User, amount: int):
        player = self.bot.player_service.get_player(ctx.author.id)
        player_coins = player.coins

        if player.id == user.id:
            raise commands.BadArgument("Cannot give coins to yourself")

        if amount < 1:
            raise commands.BadArgument("Must give at least 1 coin")

        if player_coins < amount:
            raise commands.BadArgument("Insufficient coins")

        self.bot.player_service.update_coins(player.id, -amount)
        self.bot.player_service.update_coins(user.id, amount)

        await ctx.send(content=f"Gave {user.name} {amount} coin(s)")

    @give.error
    async def give_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!give` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def flex(self, ctx):
        player = self.bot.player_service.get_player(ctx.author.id)
        flex_level = player.flex_level
        message = ""

        if flex_level == 1:
            message = f"<@{ctx.author.id}> is the coolest mofo in the world!! 😎😎😎"
        elif flex_level == 2:
            ascii_art = """```
                 ________________________
                |.----------------------.|
                ||                      ||
                ||       ______         ||
                ||     .;;;;;;;;.       ||
                ||    /;;;;;;;;;;;\     ||
                ||   /;/`    `-;;;;; . .||
                ||   |;|__  __  \;;;|   ||
                ||.-.|;| e`/e`  |;;;|   ||
                ||   |;|  |     |;;;|'--||
                ||   |;|  '-    |;;;|   ||
                ||   |;;\ --'  /|;;;|   ||
                ||   |;;;;;---'\|;;;|   ||
                ||   |;;;;|     |;;;|   ||
                ||   |;;.-'     |;;;|   ||
                ||'--|/`        |;;;|--.||
                ||;;;;    .     ;;;;.\;;||
                ||;;;;;-.;_    /.-;;;;;;||
                ||;;;;;;;;;;;;;;;;;;;;;;||
                ||jgs;;;;;;;;;;;;;;;;;;;||
                '------------------------'
            ```"""
            message = f"<@{ctx.author.id}> is so rich they can afford the Mona Lisa!\n{ascii_art}"
        else:
            message = f"Wow... {ctx.author.name} truly is pathetic."

        await ctx.send(content=message)

    # --- Helpers ---

    def use_item(self, player: Player, item: Item) -> bool:
        if item.id == "1":  # Horse insurance
            self.apply_gamble_bonus(player)
        elif item.id == "3":  # UFO horse icon
            self.apply_horse_icon(player, item.symbol)
        elif item.id == "4":  # Lips horse icon
            self.apply_horse_icon(player, item.symbol)
        elif item.id == "5":
            self.apply_flex(player, 1)
        elif item.id == "6":
            self.apply_flex(player, 2)
        else:
            return False

        if item.one_time_use:
            self.bot.player_service.remove_item(player.id, item)
        return True

    def apply_gamble_bonus(self, player: Player):
        self.bot.player_service.add_modifier(player.id, HORSE_INSURANCE_MODIFIER)

    def apply_flex(self, player: Player, flex_level: int):
        self.bot.player_service.update_flex_level(player.id, flex_level)

    def apply_horse_icon(self, player: Player, new_icon: str):
        self.bot.player_service.update_horse_icon(player.id, new_icon)
