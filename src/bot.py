import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

import wapo_api
import helper
from const import CHANNEL_ID, GITHUB_REPOSITORY, GITHUB_ICON


class WaPoBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def on_ready(self):
        print(f"{self.user} has connected!")

    async def on_command_error(self, ctx, error):
        print(f"Command error: {error}")


class WaPoBotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_generating_url = False
        self.players = {}
        self.solved = set()

    @commands.command()
    async def wapo(self, ctx):
        if CHANNEL_ID == ctx.channel.id and not self.is_generating_url:
            embed_loading = discord.Embed(
                title="Washington Post Daily Crossword",
                description="Fetching URL...",
                color=discord.Color.teal(),
            )
            embed_loading.set_footer(text=GITHUB_REPOSITORY, icon_url=GITHUB_ICON)
            message = await ctx.send(embed=embed_loading)

            try:
                self.is_generating_url = True

                url = wapo_api.get_wapo_url()
                date_str = helper.get_puzzle_date(url)
                weekday_str = helper.get_puzzle_weekday(date_str)

                embed_success = embed_loading.copy()
                embed_success.url = url
                embed_success.description = (
                    f"URL for {weekday_str} generated! ({date_str})"
                )
                embed_success.color = discord.Color.green()
                await message.edit(embed=embed_success)

            except Exception as e:
                embed_error = embed_loading.copy()
                embed_error.description = "Error fetching URL"
                embed_error.color = discord.Color.red()
                await message.edit(embed=embed_error)

                print(f"Unable to get URL: {e}")

            finally:
                self.is_generating_url = False

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return

        if reaction.message.channel.id != CHANNEL_ID:
            return

        if reaction.emoji != "👍" and reaction.emoji != "✅":
            return

        if len(reaction.embeds) == 0:
            return

        print("there is an embed")

        puzzle_link = reaction.embeds[0].description

        if not helper.is_message_url(puzzle_link):
            return

        print("the embed does contain a url")

        bot_message = await reaction.message.channel.send(
            "Checking if puzzle is complete..."
        )

        try:
            if not wapo_api.is_complete(puzzle_link):
                await bot_message.edit(content="Puzzle is not complete!")
                return
        except Exception as e:
            print(f"Unable to check puzzle is complete: {e}")
            return

        puzzle_date = helper.get_puzzle_date(puzzle_link)

        if puzzle_date in self.solved:
            await bot_message.edit(content="You already solved this crossword")
            return

        self.solved.add(puzzle_date)

        puzzle_weekday = helper.get_puzzle_weekday(puzzle_date)
        puzzle_time = wapo_api.get_puzzle_time(puzzle_link)
        puzzle_reward = helper.get_puzzle_reward(puzzle_weekday, puzzle_time)

        await bot_message.edit(
            content=f"You completed the puzzle! You get {puzzle_reward} point(s)!"
        )


async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True

    bot = WaPoBot(command_prefix="!", intents=intents)
    await bot.add_cog(WaPoBotCog(bot))
    await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
