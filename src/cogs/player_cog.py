from typing import List
import discord
from discord.ext import commands

from schemas.player import Player
from schemas.player_item import PlayerItem
from schemas.player_avatar import PlayerAvatar
from helper import get_embed, is_modifier_active, get_modifier_time_left


class PlayerCog(commands.Cog):
    """
    Gathers commands relevant for players
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="profile", description="View your profile")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def profile(self, ctx: commands.Context):
        player_id = ctx.author.id
        player = self.bot.player_service.get_player(player_id)

        # Compile player information
        name = ctx.author.name
        avatar = player.get_active_avatar() or "No avatar"
        inventory = player.get_items()
        coins = player.get_coins()
        horse_race_stats = self.bot.horse_race_service.get_horse_race_stats(player_id)
        roulette_stats = self.bot.roulette_service.get_roulette_stats(player_id)

        embed = get_embed(
            f"Profile: {name}",
            f"Player ID: {player.id}",
            discord.Color.green(),
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.add_field(name="Avatar", value=avatar, inline=False)
        embed.add_field(
            name="Inventory",
            value=f"{str(len(inventory))} item(s)",
            inline=False,
        )
        embed.add_field(name="Coins", value=str(coins), inline=True)
        embed.add_field(
            name="Horse Race Stats",
            value=horse_race_stats,
            inline=False,
        )
        embed.add_field(
            name="Roulette Stats",
            value=roulette_stats,
            inline=False,
        )
        await ctx.send(embed=embed, ephemeral=True)

    @profile.error
    async def profile_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`profile` error: {error}")

    @commands.hybrid_command(name="coins", description="Check your coin balance")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def coins(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        coins = player.get_coins()
        await ctx.send(content=f"You have {coins} coins", ephemeral=True)

    @coins.error
    async def coins_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`coins` error: {error}")

    @commands.hybrid_command(name="holdings", description="Check your holdings")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def holdings(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)

        embed = get_embed("Player Holdings", "The stocks you own", discord.Color.blue())

        for holding in player.get_holdings():
            embed.add_field(
                name=f"${holding.ticker}",
                value=f"Shares: {holding.shares}\n"
                f"Average Price: ${holding.average_price:.2f}",
                inline=False,
            )

        await ctx.send(embed=embed)

    @holdings.error
    async def holdings_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`holdings` error: {error}")

    @commands.hybrid_command(name="inventory", description="See all the items in your inventory")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def inventory(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        items = player.get_items()

        embed = get_embed(f"{ctx.author.name}'s Inventory", "", discord.Color.orange())
        embed.set_thumbnail(url=ctx.author.avatar.url)

        if items:
            for item_id, player_item in items.items():
                # Get the information about the item from the DB
                item = self.bot.item_service.get_item(item_id)
                embed.add_field(
                    name=f"{item.name} {item.symbol}",
                    value=f"x{player_item.amount}",
                    inline=False,
                )
        else:
            embed.add_field(
                name="No items", value="You have no items in your inventory."
            )

        await ctx.send(embed=embed, ephemeral=True)

    @inventory.error
    async def inventory_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`inventory` error: {error}")

    @commands.hybrid_command(name="modifiers", description="See all your modifiers")
    async def modifiers(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        modifiers = player.get_modifiers()

        embed = get_embed(f"{ctx.author.name} Modifiers", "", discord.Color.blue())
        embed.set_thumbnail(url=ctx.author.avatar.url)

        if modifiers:
            for modifier_id, player_modifier in modifiers.items():
                # Get the information about the modifier from the DB
                modifier = self.bot.modifier_service.get_modifier(modifier_id)

                if modifier.timed:
                    if not is_modifier_active(player_modifier, modifier.duration):
                        embed.add_field(
                            name=f"{modifier.name} {modifier.symbol}",
                            value="EXPIRED",
                            inline=False,
                        )
                    else:
                        time_left = get_modifier_time_left(player_modifier, modifier.duration)
                        embed.add_field(
                            name=f"{modifier.name} {modifier.symbol}",
                            value=f"Valid for {time_left}",
                            inline=False,
                        )
                elif modifier.stacking:
                    embed.add_field(
                        name=f"{modifier.name} {modifier.symbol}",
                        value=f"Stacks: {player_modifier.stacks}",
                        inline=False,
                    )
        else:
            embed.add_field(name="No modifiers", value="You have no modifiers.")

        await ctx.send(embed=embed)

    @modifiers.error
    async def modifiers_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`modifiers` error: {error}")

    @commands.hybrid_command(name="use", description="Use an item")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def use(self, ctx: commands.Context, item_name: str):
        player = self.bot.player_service.get_player(ctx.author.id)
        item = self.bot.item_service.get_item_by_name(item_name)

        if not player.

        await self.use_item(ctx, player, item)
        await ctx.send(content=f"Used {item.name}", ephemeral=True)

    @use.error
    async def use_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`use` error: {error}")

    @commands.hybrid_command(name="give", description="Send some coin to a fellow in need")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def give(self, ctx, user: discord.User, amount: int):
        if ctx.author.id == user.id:
            raise commands.BadArgument("Cannot give coins to yourself")

        if amount < 1:
            raise commands.BadArgument("Must give at least 1 coin")

        sender = self.bot.player_service.get_player(ctx.author.id)
        receiver = self.bot.player_service.get_player(user.id)

        sender.remove_coins(amount)
        receiver.add_coins(amount)

        await ctx.send(content=f"Gave {user.name} {amount} coin(s)")

    @give.error
    async def give_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`give` error: {error}")

    @commands.hybrid_command(name="flex", description="Show off your wealth, baby!")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def flex(self, ctx):
        player = self.bot.player_service.get_player(ctx.author.id)
        player_balance = player.get_coins()
        message = ""

        if player_balance >= 1000:
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
        elif player_balance >= 500:
            message = f"<@{ctx.author.id}> is the coolest mofo in the world!! 😎😎😎"
        elif player_balance >= 100:
            message = f"Mmkay, <@{ctx.author.id}> has some serious balance! #FTG 💪"
        else:
            message = f"Wow <@{ctx.author.id}>... you're trying to flex with this amount of money? 😬"

        await ctx.send(content=message)

    @flex.error
    async def flex_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`flex` error: {error}")

    @commands.hybrid_command(name="avatar", description="Change your current avatar")
    async def avatar(self, ctx: commands.Context, avatar: str):
        player = self.bot.player_service.get_player(ctx.author.id)

        if not player.has_avatar(avatar):
            raise commands.BadArgument("You do not have this avatar")

        player.set_active_avatar(avatar)
        await ctx.send(content="Updated avatar", ephemeral=True)

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`avatar` error: {error}")

    @commands.hybrid_command(name="avatars", description="See all your avatars")
    async def avatars(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        avatars = player.get_avatars()

        embed = get_embed(f"{ctx.author.name} Avatars", "", discord.Color.blue())

        if avatars:
            for avatar in sort_avatars_by_rarity(player.avatars.values()):
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
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`avatars` error: {error}")

    # --- Helpers ---

    async def use_item(self, ctx: commands.Context, player: Player, item: Item):
        if item.one_time_use:
            self.bot.player_service.remove_item(player, item)

        if item.name == "Avatar Case":
            await self.open_case(ctx, player)
        elif item.name == "Lock":
            await self.apply_lock(ctx, player, item.symbol)
        elif item.name == "Ninja Lesson":
            await self.apply_ninja_lesson(ctx, player, item.symbol)
        elif item.name == "Signal Jammer":
            await self.apply_signal_jammer(ctx, player, item.symbol)
        else:
            raise commands.BadArgument(f"Failed to use {item.name}")

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

    async def apply_lock(self, ctx: commands.Context, player: Player, symbol: str):
        self.bot.player_service.add_modifier(player, LOCK_MODIFIER, symbol)

    async def apply_ninja_lesson(
        self, ctx: commands.Context, player: Player, symbol: str
    ):
        self.bot.player_service.add_modifier(player, NINJA_LESSON_MODIFIER, symbol)

    async def apply_signal_jammer(
        self, ctx: commands.Context, player: Player, symbol: str
    ):
        self.bot.player_service.add_modifier(player, SIGNAL_JAMMER_MODIFIER, symbol)


def sort_avatars_by_rarity(avatars: List[Avatar], default_order=999):
    rarity_order = {"Common": 1, "Rare": 2, "Epic": 3, "Legendary": 4}
    return sorted(
        avatars,
        key=lambda avatar: (
            rarity_order.get(avatar.rarity, default_order),
            avatar.icon,
        ),
    )
