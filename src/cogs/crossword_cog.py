import discord
from discord.ext import commands

import wapo_api
import helper


class CrosswordCog(commands.Cog):
    """
    Gathers commands relevant for crosswords
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="wapo", description="Fetch the URL for today's daily crossword puzzle"
    )
    @commands.cooldown(1, 60, commands.BucketType.default)
    async def wapo(self, ctx: commands.Context):
        embed_loading = helper.get_embed(
            "Washington Post Daily Crossword",
            "Fetching URL...",
            discord.Color.teal(),
        )
        ctx.sent_message = await ctx.send(embed=embed_loading)

        url = wapo_api.get_wapo_url()
        date_str = helper.get_puzzle_date(url)
        weekday_str = helper.get_puzzle_weekday(date_str)

        embed_success = helper.get_embed(
            "Washington Post Daily Crossword",
            f"URL for {weekday_str} generated! ({date_str})",
            discord.Color.green(),
            url,
        )
        await ctx.sent_message.edit(embed=embed_success)

    @wapo.error
    async def wapo_error(self, ctx: commands.Context, error):
        if hasattr(ctx, "sent_message"):
            embed_error = helper.get_embed(
                "Washington Post Daily Crossword",
                "Error fetching URL",
                discord.Color.red(),
            )
            await ctx.sent_message.edit(embed=embed_error)
        elif isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`wapo` error: {error}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user == self.bot.user:
            return

        if reaction.emoji not in ("👍", "✅"):
            return

        if len(reaction.message.embeds) == 0:
            return

        crossword_link = reaction.message.embeds[0].url

        if not helper.is_message_url(crossword_link):
            return

        embed_loading = helper.get_embed(
            "Crossword Checker",
            "Checking if crossword is complete...",
            discord.Color.teal(),
        )
        message = await reaction.message.channel.send(embed=embed_loading)

        crossword_date = helper.get_puzzle_date(crossword_link)

        if self.bot.crossword_service.has_crossword(crossword_date):
            embed_warning = helper.get_embed(
                "Crossword Checker",
                "Crossword is already solved",
                discord.Color.orange(),
            )
            await message.edit(embed=embed_warning)
            return

        try:
            puzzle_time = wapo_api.get_puzzle_time(crossword_link)
        except Exception:
            embed_error = helper.get_embed(
                "Crossword Checker", "Crossword is not complete", discord.Color.red()
            )
            await message.edit(embed=embed_error)
            return

        puzzle_weekday = helper.get_puzzle_weekday(crossword_date)
        puzzle_reward = helper.get_puzzle_reward(puzzle_weekday, puzzle_time)

        self.bot.crossword_service.add_crossword(crossword_date, puzzle_time)

        players = self.bot.player_service.get_players()
        crossword_boost_modifier = self.bot.modifier_service.get_modifier("crossword_booster")

        for player in players:
            # Increase the reward for players with a Crossword Booster
            if player.is_modifier_valid(crossword_boost_modifier):
                player.add_coins(round(puzzle_reward * 1.5))
            else:
                player.add_coins(puzzle_reward)

        embed_success = helper.get_embed(
            "Crossword Checker",
            (
                "Crossword complete!"
                f" Completed in {helper.format_seconds(puzzle_time)},"
                f" {puzzle_reward} coin(s)"
                f" rewarded to {len(players)} players."
            ),
            discord.Color.green(),
        )

        await message.edit(embed=embed_success)

        # Start happy hour event if the crossword is complete
        for player in players:
            player.add_modifier("happy_hour")

        embed_happy_hour = helper.get_embed("🍻 Happy Hour 🍻", "Happy hour is starting now!", discord.Color.green())
        message = await reaction.message.channel.send(embed=embed_happy_hour)
