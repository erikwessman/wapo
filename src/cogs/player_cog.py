import discord
from discord.ext import commands

from helper import get_embed


class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def register(self, ctx: commands.Context):
        author_id = ctx.author.id
        author_name = ctx.author.name

        if self.bot.player_manager.has_player(author_id):
            raise commands.CommandError(f"{author_name} already registered")

        self.bot.player_manager.set_tokens(author_id, 0)
        await ctx.send(content=f"Registered {author_name}")

    @register.error
    async def register_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!register` error: {error}")

    @commands.command()
    async def profile(self, ctx: commands.Context):
        pass

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tokens(self, ctx: commands.Context):
        author_id = ctx.author.id
        author_tokens = self.bot.player_manager.get_tokens(author_id)
        await ctx.send(content=f"You have {author_tokens} tokens")

    @commands.command()
    async def items(self, ctx: commands.Context):
        author_id = ctx.author.id
        player = self.bot.player_manager.get_player(author_id)
        await ctx.send("\n".join(player.items))

    @commands.command()
    async def send(self, ctx, user: discord.User, amount: int):
        author_id = ctx.author.id
        author_tokens = self.bot.player_manager.get_tokens(author_id)

        if author_id == user.id:
            raise commands.BadArgument("Cannot send tokens to yourself")

        if amount < 1:
            raise commands.BadArgument("Cannot send less than 1 token")

        if author_tokens < amount:
            raise commands.BadArgument("Insufficient tokens")

        self.bot.player_manager.update_tokens(author_id, -amount)
        self.bot.player_manager.update_tokens(user.id, amount)

        await ctx.send(content=f"Gave {user.name} {amount} token(s)")

    @send.error
    async def send_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!send` error: {error}")
