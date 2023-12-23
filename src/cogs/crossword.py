import discord
from discord.ext import commands

import wapo_api
import helper
from helper import get_embed
from const import CHANNEL_ID


class CrosswordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.default)
    async def wapo(self, ctx: commands.Context):
        if CHANNEL_ID == ctx.channel.id:
            embed_loading = get_embed(
                "Washington Post Daily Crossword",
                "Fetching URL...",
                discord.Color.teal(),
            )
            ctx.sent_message = await ctx.send(embed=embed_loading)

            try:
                url = wapo_api.get_wapo_url()
                date_str = helper.get_puzzle_date(url)
                weekday_str = helper.get_puzzle_weekday(date_str)

                embed_success = get_embed(
                    "Washington Post Daily Crossword",
                    f"URL for {weekday_str} generated! ({date_str})",
                    discord.Color.green(),
                    url,
                )
                await ctx.sent_message.edit(embed=embed_success)

            except Exception as error:
                raise commands.CommandError("An error occurred.") from error

    @wapo.error
    async def wapo_error(self, ctx: commands.Context, error):
        if hasattr(ctx, "sent_message"):
            embed_error = get_embed(
                "Washington Post Daily Crossword",
                "Error fetching URL",
                discord.Color.red(),
            )
            await ctx.sent_message.edit(embed=embed_error)
        else:
            await ctx.send(f"An error occurred: {error}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user == self.bot.user or reaction.message.channel.id != CHANNEL_ID:
            return

        if reaction.emoji not in ("👍", "✅"):
            return

        if len(reaction.message.embeds) == 0:
            return

        puzzle_link = reaction.message.embeds[0].url

        if not helper.is_message_url(puzzle_link):
            return

        embed_loading = get_embed(
            "Crossword Checker",
            "Checking if crossword is complete...",
            discord.Color.teal(),
        )
        message = await reaction.message.channel.send(embed=embed_loading)

        puzzle_date = helper.get_puzzle_date(puzzle_link)

        if self.bot.crossword_manager.has_crossword(puzzle_date):
            embed_warning = get_embed(
                "Crossword Checker",
                "Crossword is already solved",
                discord.Color.orange(),
            )
            await message.edit(embed=embed_warning)
            return

        if not wapo_api.is_complete(puzzle_link):
            embed_error = get_embed(
                "Crossword Checker",
                "Crossword is not complete",
                discord.Color.red()
            )
            await message.edit(embed=embed_error)
            return

        self.bot.crossword_manager.save_crossword(puzzle_date)

        puzzle_weekday = helper.get_puzzle_weekday(puzzle_date)
        puzzle_time = wapo_api.get_puzzle_time(puzzle_link)
        puzzle_reward = helper.get_puzzle_reward(puzzle_weekday, puzzle_time)

        players = self.bot.token_manager.get_players()

        for player in players:
            self.bot.token_manager.update_tokens(player, puzzle_reward)

        embed_success = get_embed(
            "Crossword Checker",
            (
                f"Crossword complete! {puzzle_reward} token(s)"
                f" rewarded to {len(players)} players"
            ),
            discord.Color.green(),
        )

        await message.edit(embed=embed_success)
