import discord
from discord.ext import commands

from store import Store
from helper import get_embed


class StoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.store = Store("src/store_items.json")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def store(self, ctx: commands.Context):
        await ctx.send("\n".join(self.store.items))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def buy(self, ctx: commands.Context):
        pass
