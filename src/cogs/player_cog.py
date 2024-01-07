import discord
from discord.ext import commands

from schemas.item import Item
from schemas.player import Player
from helper import get_embed
from const import HORSE_INSURANCE_MODIFIER


class PlayerCog(commands.Cog):
    """
    Gathers commands relevant for players
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="profile", description="View your profile")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def profile(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        name = ctx.author.name
        avatar = player.active_avatar
        inventory = player.inventory
        coins = player.coins

        embed = get_embed(
            f"Profile: {name}",
            f"Player ID: {player.id}",
            discord.Color.green(),
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(
            name="Avatar", value=f"{avatar or 'No custom avatar'}", inline=False
        )
        embed.add_field(
            name="Inventory",
            value=f"{str(len(inventory))} item(s)",
            inline=False,
        )
        embed.add_field(name="Coins", value=str(coins), inline=True)

        await ctx.send(embed=embed, ephemeral=True)

    @profile.error
    async def profile_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`profile` error: {error}")

    @commands.hybrid_command(name="coins", description="Check your coin balance")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def coins(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        await ctx.send(content=f"You have {player.coins} coins", ephemeral=True)

    @coins.error
    async def coins_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`coins` error: {error}")

    @commands.hybrid_command(name="holdings", description="Check your holdings")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def holdings(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)

        embed = get_embed("Player Holdings", "", discord.Color.blue())

        for holding in player.holdings.values():
            embed.add_field(
                name=f"${holding.ticker}",
                value=f"Shares: {holding.shares}\n"
                f"Average Price: ${holding.average_price:.2f}",
                inline=False,
            )

        await ctx.send(embed=embed)

    @holdings.error
    async def holdings_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`holdings` error: {error}")

    @commands.hybrid_command(
        name="inventory", description="See all the items in your inventory"
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def inventory(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        inventory = player.inventory

        embed = get_embed(f"{ctx.author.name}'s Inventory", "", discord.Color.orange())
        embed.set_thumbnail(url=ctx.author.avatar.url)

        if inventory:
            for item_id, quantity in inventory.items():
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

        await ctx.send(embed=embed, ephemeral=True)

    @inventory.error
    async def inventory_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`inventory` error: {error}")

    @commands.hybrid_command(name="use", description="Use an item")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def use(self, ctx: commands.Context, item_id: str):
        player = self.bot.player_service.get_player(ctx.author.id)
        item = self.bot.store.get_item(item_id)

        await self.use_item(ctx, player, item)
        await ctx.send(content=f"Used {item.name}", ephemeral=True)

    @use.error
    async def use_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`use` error: {error}")

    @commands.hybrid_command(
        name="give", description="Send some coin to a fellow in need"
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def give(self, ctx, user: discord.User, amount: int):
        if ctx.author.id == user.id:
            raise commands.BadArgument("Cannot give coins to yourself")

        if amount < 1:
            raise commands.BadArgument("Must give at least 1 coin")

        sender = self.bot.player_service.get_player(ctx.author.id)
        receiver = self.bot.player_service.get_player(user.id)

        self.bot.player_service.remove_coins(sender, amount)
        self.bot.player_service.add_coins(receiver, amount)

        await ctx.send(content=f"Gave {user.name} {amount} coin(s)")

    @give.error
    async def give_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`give` error: {error}")

    @commands.hybrid_command(name="flex", description="Show off your wealth, baby!")
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
                ||;;;;;;;;;;;;;;;;;;;;;;||
                '------------------------'
            ```"""
            message = f"<@{ctx.author.id}> is so rich they can afford the Mona Lisa!\n{ascii_art}"
        else:
            message = f"Wow... {ctx.author.name} truly is pathetic."

        await ctx.send(content=message)

    @flex.error
    async def flex_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`flex` error: {error}")

    @commands.hybrid_command(name="avatar", description="Change your current avatar")
    async def avatar(self, ctx: commands.Context, avatar: str):
        player = self.bot.player_service.get_player(ctx.author.id)
        self.bot.player_service.update_avatar(player, avatar)
        await ctx.send(content="Updated avatar", ephemeral=True)

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`avatar` error: {error}")

    @commands.hybrid_command(name="avatars", description="See all your avatars")
    async def avatars(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        embed = get_embed(f"{ctx.author.name} Avatars", "", discord.Color.blue())

        if player.avatars:
            for avatar in player.avatars.values():
                embed.add_field(
                    name=f"{avatar.icon} - {avatar.rarity} (x{avatar.count})",
                    value="",
                    inline=False,
                )
        else:
            embed.add_field(name="No avatars", value="You have no avatars.")
        await ctx.send(embed=embed)

    @avatars.error
    async def avatars_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`avatars` error: {error}")

    # --- Helpers ---

    async def use_item(self, ctx: commands.Context, player: Player, item: Item):
        if item.one_time_use:
            self.bot.player_service.remove_item(player, item)

        if item.id == "1":
            self.apply_gamble_bonus(player)
        elif item.id == "3":
            self.apply_flex(player, 1)
        elif item.id == "4":
            self.apply_flex(player, 2)
        elif item.id == "5":
            await self.open_case(ctx, player)
        else:
            raise commands.CommandError("Failed to use item")

    def apply_gamble_bonus(self, player: Player):
        self.bot.player_service.add_modifier(player, HORSE_INSURANCE_MODIFIER)

    def apply_flex(self, player: Player, flex_level: int):
        self.bot.player_service.update_flex_level(player, flex_level)

    async def open_case(self, ctx: commands.Context, player: Player):
        rarity, icon = self.bot.case_api.get_case_item()

        self.bot.player_service.add_avatar(player, icon, rarity)

        rarity_colors = {
            "Common": 0xFFFFFF,
            "Rare": discord.Color.blue(),
            "Epic": discord.Color.purple(),
            "Legendary": discord.Color.orange(),
        }

        embed = get_embed("Case Opened!", "", rarity_colors.get(rarity, 0xFFFFFF))
        embed.add_field(
            name="Congratulations!", value=f"You got a {rarity} {icon}!", inline=False
        )
        await ctx.send(embed=embed)
