import discord
from discord.ext import commands

from classes.store import Store
from helper import get_embed


class StoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.store = Store("data/items.json")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def store(self, ctx: commands.Context):
        items = self.store.items
        embed = get_embed("Store", "Buy cool stuff", discord.Color.pink())

        for item in items:
            item_details = (
                f"{item.symbol}\n"
                f"**Title:** {item.title}\n"
                f"**Description:** {item.description}\n"
                f"**Price:** {item.price} tokens\n"
                f"**One Time Use:** {'Yes' if item.one_time_use else 'No'}"
            )
            embed.add_field(
                name=f"Item ID: {item.item_id}", value=item_details, inline=False
            )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def buy(self, ctx: commands.Context, item_id: int):
        author_id = ctx.author.id

        self.bot.player_manager.handle_buy_item(author_id, item_id)
