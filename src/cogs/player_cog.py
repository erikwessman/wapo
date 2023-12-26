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
        player = self.bot.player_service.get_player(author_id)
        player_items = player.items
        player_tokens = player.tokens

        embed = get_embed(
            f"Profile: {author_name}",
            f"Player ID: {author_id}",
            discord.Color.orange(),
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(name="Items", value=str(len(player_items)), inline=False)
        embed.add_field(name="Tokens", value=str(player_tokens), inline=True)

        await ctx.send(embed=embed)

    @profile.error
    async def profile_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!profile` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tokens(self, ctx: commands.Context):
        author_id = ctx.author.id
        player = self.bot.player_service.get_player(author_id)
        await ctx.send(content=f"You have {player.tokens} tokens")

    @tokens.error
    async def tokens_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!tokens` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def items(self, ctx: commands.Context):
        author_id = ctx.author.id
        player = self.bot.player_service.get_player(author_id)
        player_items = player.items

        embed = discord.Embed(
            title=f"{ctx.author.name}'s Items", color=discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)

        if player_items:
            for item, quantity in player_items.items():
                embed.add_field(name=item, value=f"Quantity: {quantity}", inline=False)
        else:
            embed.add_field(
                name="No items", value="You have no items in your inventory."
            )

        await ctx.send(embed=embed)

    @items.error
    async def items_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!items` error: {error}")

    @commands.command()
    async def send(self, ctx, user: discord.User, amount: int):
        author_id = ctx.author.id
        player = self.bot.player_service.get_player(author_id)
        player_tokens = player.tokens

        if author_id == user.id:
            raise commands.BadArgument("Cannot send tokens to yourself")

        if amount < 1:
            raise commands.BadArgument("Must send at least 1 token")

        if player_tokens < amount:
            raise commands.BadArgument("Insufficient tokens")

        self.bot.player_manager.update_tokens(author_id, -amount)
        self.bot.player_manager.update_tokens(user.id, amount)

        await ctx.send(content=f"Sent {user.name} {amount} token(s)")

    @send.error
    async def send_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!send` error: {error}")
