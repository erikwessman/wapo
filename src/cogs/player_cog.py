from typing import List
from datetime import datetime
import discord
from discord.ext import commands

from schemas.item import Item
from schemas.avatar import Avatar
from schemas.player import Player
from helper import get_embed
from const import LOCK_MODIFIER, NINJA_LESSON_MODIFIER, SIGNAL_JAMMER_MODIFIER


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
        avatar = player.active_avatar or "No avatar"
        inventory = player.inventory
        coins = player.coins
        horse_race_stats = self.get_horse_race_stats(player.id)
        roulette_stats = self.get_roulette_stats(player.id)

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
        await ctx.send(content=f"You have {player.coins} coins", ephemeral=True)

    @coins.error
    async def coins_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
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
        if isinstance(error, commands.BadArgument):
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
            for item_name, quantity in inventory.items():
                item = self.bot.store.get_item(item_name, False)
                embed.add_field(
                    name=f"{item.name} {item.symbol}",
                    value=f"x{quantity}",
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

    @commands.hybrid_command(name="use", description="Use an item")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def use(self, ctx: commands.Context, item_name: str):
        player = self.bot.player_service.get_player(ctx.author.id)
        item = self.bot.store.get_item(item_name)

        await self.use_item(ctx, player, item)
        await ctx.send(content=f"Used {item.name}", ephemeral=True)

    @use.error
    async def use_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
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
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`give` error: {error}")

    @commands.hybrid_command(name="flex", description="Show off your wealth, baby!")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def flex(self, ctx):
        player = self.bot.player_service.get_player(ctx.author.id)
        player_balance = player.coins
        message = ""

        if player_balance >= 250:
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
        elif player_balance >= 100:
            message = f"<@{ctx.author.id}> is the coolest mofo in the world!! 😎😎😎"
        elif player_balance >= 50:
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
        self.bot.player_service.update_avatar(player, avatar)
        await ctx.send(content="Updated avatar", ephemeral=True)

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`avatar` error: {error}")

    @commands.hybrid_command(name="avatars", description="See all your avatars")
    async def avatars(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        embed = get_embed(f"{ctx.author.name} Avatars", "", discord.Color.blue())

        if player.avatars:
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

    @commands.hybrid_command(name="modifiers", description="See all your modifiers")
    async def modifiers(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        embed = get_embed(f"{ctx.author.name} Modifiers", "", discord.Color.blue())

        now = datetime.utcnow()

        if player.modifiers:
            for modifier in player.modifiers.values():
                hours_difference = (now - modifier.last_used).total_seconds() / 3600
        else:
            embed.add_field(name="No modifiers", value="You have no modifiers.")
        await ctx.send(embed=embed)

    @modifiers.error
    async def modifiers_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`modifiers` error: {error}")

    # --- Helpers ---

    def get_horse_race_stats(self, player_id: int) -> str:
        horse_races = self.bot.horse_race_service.get_player_horse_races(player_id)
        if horse_races:
            total_bet = sum(h.bet for h in horse_races)
            total_win = sum(h.win for h in horse_races)
            max_win = max(max((h.win - h.bet) for h in horse_races), 0)
            max_loss = max(max((h.bet - h.win) for h in horse_races), 0)

            return (
                f"Total bet: {total_bet}\n"
                f"Total win: {total_win}\n"
                f"Biggest win: {max_win}\n"
                f"Biggest loss: {max_loss}"
            )
        else:
            return "No Horse Race data"

    def get_roulette_stats(self, player_id: int) -> str:
        roulettes = self.bot.roulette_service.get_roulettes_by_player(player_id)
        total_bet = 0
        total_win = 0
        max_win = 0
        max_loss = 0

        if not roulettes:
            return "No Roulette data"

        for roulette in roulettes:
            player_bet = roulette.players.get(str(player_id), 0)
            total_bet += player_bet

            if roulette.winner == player_id:
                total_pool = sum(roulette.players.values()) - player_bet
                total_win += total_pool
                max_win = max(max_win, total_pool)
            else:
                max_loss = max(max_loss, player_bet)

        return (
            f"Total bet: {total_bet}\n"
            f"Total win: {total_win}\n"
            f"Biggest win: {max_win}\n"
            f"Biggest loss: {max_loss}"
        )

    async def use_item(self, ctx: commands.Context, player: Player, item: Item):
        if item.one_time_use:
            self.bot.player_service.remove_item(player, item)

        if item.name == "Avatar Case":
            await self.open_case(ctx, player)
        elif item.name == "Lock":
            await self.apply_lock(ctx, player)
        elif item.name == "Ninja Lesson":
            await self.apply_ninja_lesson(ctx, player)
        elif item.name == "Signal Jammer":
            await self.apply_signal_jammer(ctx, player)
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

    async def apply_lock(self, ctx: commands.Context, player: Player):
        self.bot.player_service.add_modifier(player, LOCK_MODIFIER)

    async def apply_ninja_lesson(self, ctx: commands.Context, player: Player):
        self.bot.player_service.add_modifier(player, NINJA_LESSON_MODIFIER)

    async def apply_signal_jammer(self, ctx: commands.Context, player: Player):
        self.bot.player_service.add_modifier(player, SIGNAL_JAMMER_MODIFIER)


def sort_avatars_by_rarity(avatars: List[Avatar], default_order=999):
    rarity_order = {'Common': 1, 'Rare': 2, 'Epic': 3, 'Legendary': 4}
    return sorted(avatars, key=lambda avatar: (rarity_order.get(avatar.rarity, default_order), avatar.icon))
