import discord
from discord.ext import commands

from classes.item import Item
from classes.player import Player
from helper import get_embed
from const import HORSIE_STEROIDS_MODIFIER_NAME


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
        player_tokens = player.tokens

        embed = get_embed(
            f"Profile: {player_name}",
            f"Player ID: {player.id}",
            discord.Color.green(),
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(
            name="Inventory", value=f"{str(len(player_inventory))} item(s)", inline=False
        )
        embed.add_field(name="Tokens", value=str(player_tokens), inline=True)

        await ctx.send(embed=embed)

    @profile.error
    async def profile_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!profile` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tokens(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        await ctx.send(content=f"You have {player.tokens} tokens")

    @tokens.error
    async def tokens_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!tokens` error: {error}")

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
    async def send(self, ctx, user: discord.User, amount: int):
        player = self.bot.player_service.get_player(ctx.author.id)
        player_tokens = player.tokens

        if player.id == user.id:
            raise commands.BadArgument("Cannot send tokens to yourself")

        if amount < 1:
            raise commands.BadArgument("Must send at least 1 token")

        if player_tokens < amount:
            raise commands.BadArgument("Insufficient tokens")

        self.bot.player_service.update_tokens(player.id, -amount)
        self.bot.player_service.update_tokens(user.id, amount)

        await ctx.send(content=f"Sent {user.name} {amount} token(s)")

    @send.error
    async def send_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!send` error: {error}")

    # --- Helpers ---

    def use_item(self, player: Player, item: Item) -> bool:
        if item.id == "1":  # Horsie steroids
            self.apply_gamble_bonus(player)
        else:
            return False

        self.bot.player_service.remove_item(player.id, item)
        return True

    def apply_gamble_bonus(self, player: Player):
        self.bot.player_service.add_modifier(player.id, HORSIE_STEROIDS_MODIFIER_NAME)
