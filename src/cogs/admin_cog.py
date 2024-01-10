import os
from discord.ext import commands


class AdminCog(commands.Cog):
    _NOT_DEV_MODE_MSG = "This command is only available in dev mode"

    def __init__(self, bot):
        self.bot = bot

    def is_dev_mode(self):
        dev_mode = os.getenv("DEV_MODE")
        if dev_mode is None:
            return False

        return dev_mode.lower() == "true"

    @commands.hybrid_command(name="dev-ping", description="Ping, pong!")
    async def dev_ping(self, ctx: commands.Context):
        if not self.is_dev_mode():
            await ctx.send(content=self._NOT_DEV_MODE_MSG, ephemeral=True)
            return

        await ctx.send(content="Pong!", ephemeral=True)
