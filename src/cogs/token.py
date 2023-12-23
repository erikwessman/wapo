import discord
from discord.ext import commands


class TokenCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def send(self, ctx, user: discord.User, amount: int):
        author_id = ctx.author.id
        author_tokens = self.bot.token_manager.get_tokens(author_id)

        if author_id == user.id:
            raise commands.BadArgument("Cannot send tokens to yourself")

        if amount < 1:
            raise commands.BadArgument("Cannot send less than 1 token")

        if author_tokens < amount:
            raise commands.BadArgument("Insufficient tokens")

        self.bot.token_manager.update_tokens(author_id, -amount)
        self.bot.token_manager.update_tokens(user.id, amount)

        await ctx.send(content=f"Gave {user.name} {amount} token(s)")

    @send.error
    async def send_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!send` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def register(self, ctx: commands.Context):
        author_id = ctx.author.id
        author_name = ctx.author.name

        if self.bot.token_manager.has_player(author_id):
            raise commands.CommandError(f"{author_name} already registered")

        self.bot.token_manager.set_tokens(author_id, 0)
        await ctx.send(content=f"Registered {author_name}")

    @register.error
    async def register_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!register` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tokens(self, ctx: commands.Context):
        author_id = ctx.author.id
        author_tokens = self.bot.token_manager.get_tokens(author_id)
        await ctx.send(content=f"You have {author_tokens} tokens")
