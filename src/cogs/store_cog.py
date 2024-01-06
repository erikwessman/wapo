import discord
from discord.ext import commands

from helper import get_embed


class StoreCog(commands.Cog):
    """
    Gathers commands relevant for interacting with the store
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="store", description="View the item store")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def store(self, ctx: commands.Context):
        items = self.bot.store.get_items()
        embed = get_embed("Store", "Buy cool stuff", discord.Color.pink())

        for item in items:
            item_details = (
                f"**Item ID:** {item.id}\n"
                f"**Description:** {item.description}\n"
                f"**Price:** {item.price} coins\n"
                f"**One Time Use:** {'Yes' if item.one_time_use else 'No'}"
            )
            embed.add_field(
                name=f"Item Name: {item.name} {item.symbol}",
                value=item_details,
                inline=False,
            )

        await ctx.send(embed=embed, ephemeral=True)

    @store.error
    async def store_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`store` error: {error}")

    @commands.hybrid_command(name="", description="")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cases(self, ctx: commands.Context):
        embed = get_embed("Case Odds & Items", "", discord.Color.red())
        tiers = self.bot.case_api.get_tiers()

        for tier, tier_info in tiers.items():
            items_string = " ".join(tier_info["items"])
            embed.add_field(
                name=f"{tier} {tier_info['drop_rate']}%",
                value=items_string,
                inline=False,
            )

        await ctx.send(embed=embed)

    @cases.error
    async def cases_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`cases` error: {error}")

    @commands.hybrid_command(name="buy", description="Buy an item from the store")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def buy(self, ctx: commands.Context, item_id: str, quantity: int = 1):
        if quantity < 1:
            raise commands.CommandError("Must buy at least 1 item")

        player = self.bot.player_service.get_player(ctx.author.id)
        item = self.bot.store.get_item(item_id)

        self.bot.player_service.buy_item(player, item, quantity)

        await ctx.send(content=f"Bought {quantity} {item.name}(s)")

    @buy.error
    async def buy_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`buy` error: {error}")
