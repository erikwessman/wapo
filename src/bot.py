import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

import wapo_api
import helper
from const import CHANNEL_ID, GITHUB_REPOSITORY, GITHUB_ICON


load_dotenv()


def main():
    # Allow one !wapo request at a time
    is_generating_url = False

    players = {}
    solved = set()

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(intents=intents, command_prefix="!")

    @bot.command()
    async def wapo(ctx):
        global is_generating_url

        if CHANNEL_ID == ctx.channel.id and not is_generating_url:
            embed_loading = discord.Embed(
                title="Washington Post Daily Crossword",
                description="Fetching URL...",
                color=discord.Color.teal(),
            )
            embed_loading.set_footer(text=GITHUB_REPOSITORY, icon_url=GITHUB_ICON)
            message = await ctx.send(embed=embed_loading)

            try:
                is_generating_url = True
                url = wapo_api.get_wapo_url()

                embed_success = embed_loading.copy()
                embed_success.url = url
                embed_success.description = "URL generated!"
                embed_success.color = discord.Color.green()

                await message.edit(embed=embed_success)

            except Exception:
                embed_error = embed_loading.copy()
                embed_error.description = "Error fetching URL"
                embed_error.color = discord.Color.red()

                await message.edit(embed=embed_error)

            finally:
                is_generating_url = False

    @bot.event
    async def on_reaction_add(reaction, user):
        if reaction.message.author == bot.user:

            if reaction.message.channel.id != CHANNEL_ID:
                return

            if reaction.emoji != "👍" and reaction.emoji != "✅":
                return

            if len(reaction.embeds) == 0:
                return

            puzzle_link = reaction.embeds[0].description

            if not helper.is_message_url(puzzle_link):
                return

            bot_message = await reaction.message.channel.send(
                "Checking if puzzle is complete..."
            )

            if not wapo_api.is_complete(puzzle_link):
                await bot_message.edit(content="Puzzle is not complete!")
                return

            puzzle_date = helper.get_puzzle_date(puzzle_link)

            if puzzle_date in solved:
                await bot_message.edit(content="You already solved this crossword")
                return

            solved.add(puzzle_date)

            puzzle_weekday = helper.get_puzzle_weekday(puzzle_date)
            puzzle_time = wapo_api.get_puzzle_time(puzzle_link)
            puzzle_reward = helper.get_puzzle_reward(puzzle_weekday, puzzle_time)

            await bot_message.edit(
                content=f"You completed the puzzle! You get {puzzle_reward} point(s)!"
            )

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
