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
        await ctx.send("\n".join(self.store.items))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def buy(self, ctx: commands.Context, item_id: int):
        author_id = ctx.author.id
        self.bot.player_manager.add_item_to_player(author_id, item_id)
