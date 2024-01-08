from discord.ext import commands


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="helloworld", description="Says hello to the world")
    async def helloworld(self, ctx: commands.Context):
        await ctx.send(embed="hello world", ephemeral=True)
