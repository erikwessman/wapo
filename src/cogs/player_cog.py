import discord
from discord.ext import commands

from helper import get_embed


class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def profile(self, ctx: commands.Context):
        author_id = ctx.author.id
        author_name = ctx.author.name
        player = self.bot.player_manager.get_player(author_id)

        embed = get_embed(
            f"Profile: {author_name}",
            f"Player ID: {player.player_id}",
            discord.Color.orange(),
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)

        item_text = "\n".join(
            f"{item}: {quantity}" for item, quantity in player.items.items()
        )
        item_text = item_text if item_text else "No items."

        embed.add_field(name="Items", value=item_text, inline=False)
        embed.add_field(name="Tokens", value=str(player.tokens), inline=True)

        await ctx.send(embed=embed)

    @profile.error
    async def profile_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!profile` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tokens(self, ctx: commands.Context):
        author_id = ctx.author.id
        author_tokens = self.bot.player_manager.get_tokens(author_id)
        await ctx.send(content=f"You have {author_tokens} tokens")

    @tokens.error
    async def tokens_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!tokens` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def items(self, ctx: commands.Context):
        author_id = ctx.author.id
        player_items = self.bot.player_manager.get_player_items(author_id)

        item_text = "\n".join(
            f"{item}: {quantity}" for item, quantity in player_items.items()
        )
        item_text = item_text if item_text else "No items."

        await ctx.send(content=item_text)

    @items.error
    async def items_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!items` error: {error}")

    @commands.command()
    async def send(self, ctx, user: discord.User, amount: int):
        author_id = ctx.author.id
        author_tokens = self.bot.player_manager.get_tokens(author_id)

        if author_id == user.id:
            raise commands.BadArgument("Cannot send tokens to yourself")

        if amount < 1:
            raise commands.BadArgument("Must send at least 1 token")

        if author_tokens < amount:
            raise commands.BadArgument("Insufficient tokens")

        self.bot.player_manager.update_tokens(author_id, -amount)
        self.bot.player_manager.update_tokens(user.id, amount)

        await ctx.send(content=f"Sent {user.name} {amount} token(s)")

    @send.error
    async def send_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!send` error: {error}")
