from discord.ext import commands

from const import DAILY_REWARD, WEEKLY_REWARD


class RewardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="daily", description="Get your daily coins")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        self.bot.player_service.add_coins(player, DAILY_REWARD)
        await ctx.send(content=f"Received {DAILY_REWARD} coins", ephemeral=True)

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`daily` error: {error}")

    @commands.hybrid_command(name="weekly", description="Get your weekly coins")
    @commands.cooldown(1, 86400 * 7, commands.BucketType.user)
    async def weekly(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        self.bot.player_service.add_coins(player, WEEKLY_REWARD)
        await ctx.send(content=f"Received {WEEKLY_REWARD} coins", ephemeral=True)

    @weekly.error
    async def weekly_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`weekly` error: {error}")
