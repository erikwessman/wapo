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
        if user == self.bot.user or reaction.message.channel.id != CHANNEL_ID:
            return

        if reaction.emoji != "👍" and reaction.emoji != "✅":
            return

        if len(reaction.message.embeds) == 0:
            return

        puzzle_link = reaction.message.embeds[0].url

        if not helper.is_message_url(puzzle_link):
            return

        embed_loading = discord.Embed(
            title="Crossword Checker",
            description="Checking if crossword is complete...",
            color=discord.Color.teal(),
        )
        embed_loading.set_footer(text=GITHUB_REPOSITORY, icon_url=GITHUB_ICON)
        message = await reaction.message.channel.send(embed=embed_loading)

        if not wapo_api.is_complete(puzzle_link):
            embed_error = embed_loading.copy()
            embed_error.description = "Crossword is not complete"
            embed_error.color = discord.Color.red()
            await message.edit(embed=embed_error)
            return

        puzzle_date = helper.get_puzzle_date(puzzle_link)

        if puzzle_date in self.solved:
            embed_warning = embed_loading.copy()
            embed_warning.description = "Crossword is already solved"
            embed_warning.color = discord.Color.orange()
            await message.edit(embed=embed_warning)
            return

        self.solved.add(puzzle_date)

        puzzle_weekday = helper.get_puzzle_weekday(puzzle_date)
        puzzle_time = wapo_api.get_puzzle_time(puzzle_link)
        puzzle_reward = helper.get_puzzle_reward(puzzle_weekday, puzzle_time)

        embed_success = embed_loading.copy()
        embed_success.description = (
            f"Crossword complete! You get {puzzle_reward}x token(s)! 🪙"
        )
        embed_success.color = discord.Color.green()
        await message.edit(embed=embed_success)


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
