import discord
from discord.ext import commands

from helper import get_embed


class StoreCog(commands.Cog):
    """
    Gathers commands relevant for interacting with the store
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def store(self, ctx: commands.Context):
        items = self.bot.store.get_items()
        embed = get_embed("Store", "Buy cool stuff", discord.Color.pink())

        for item in items:
            item_details = (
                f"**Item ID:** {item.id}\n"
                f"**Description:** {item.description}\n"
                f"**Price:** {item.price} tokens\n"
                f"**One Time Use:** {'Yes' if item.one_time_use else 'No'}"
            )
            embed.add_field(
                name=f"Item Name: {item.name} {item.symbol}",
                value=item_details,
                inline=False,
            )

        await ctx.send(embed=embed)

    @store.error
    async def store_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!store` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def buy(self, ctx: commands.Context, item_id: int, quantity: int = 1):
        player = self.bot.player_service.get_player(ctx.author.id)

        if not self.bot.store.has_item(item_id):
            raise commands.CommandError(f"Item with id {item_id} doesn't exist")

        if quantity < 1:
            raise commands.CommandError("Must buy at least 1 copy of item")

        item = self.bot.store.get_item(item_id)

        if player.tokens < item.price * quantity:
            raise commands.CommandError("Insufficient tokens")

        self.bot.player_service.buy_item(player.id, item, quantity)

        await ctx.send(content=f"Bought {quantity} {item.name}")

    @buy.error
    async def buy_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!buy` error: {error}")
