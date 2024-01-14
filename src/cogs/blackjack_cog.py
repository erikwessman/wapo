import discord
from discord.ext import commands
from helper import get_embed


class BlackjackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="blackjack", description="Play blackjack")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def store(self, ctx: commands.Context):
        embed = get_embed("Blackjack", "Play blackjack", discord.Color.pink())

        await ctx.send(embed=embed, ephemeral=True)
