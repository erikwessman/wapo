import os
import time
import math
import random
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

import wapo_api
import helper
from const import (
    CHANNEL_ID,
    GITHUB_REPOSITORY,
    GITHUB_ICON,
    EMOJI_SUNGLASSES,
    EMOJI_HEART_EYES,
    EMOJI_THINKING,
    EMOJI_GRINNING,
)


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
            embed_loading = get_embed(
                "Washington Post Daily Crossword",
                "Fetching URL...",
                discord.Color.teal(),
            )
            message = await ctx.send(embed=embed_loading)

            try:
                self.is_generating_url = True

                url = wapo_api.get_wapo_url()
                date_str = helper.get_puzzle_date(url)
                weekday_str = helper.get_puzzle_weekday(date_str)

                embed_success = get_embed(
                    "Washington Post Daily Crossword",
                    f"URL for {weekday_str} generated! ({date_str})",
                    discord.Color.green(),
                    url,
                )
                await message.edit(embed=embed_success)

            except Exception as e:
                embed_error = get_embed(
                    "Washington Post Daily Crossword",
                    "Error fetching URL",
                    discord.Color.red(),
                )
                await message.edit(embed=embed_error)

                print(f"Unable to get URL: {e}")

            finally:
                self.is_generating_url = False

    @commands.command()
    async def gamble(self, ctx, bet_index, bet_amount):
        try:
            bet_index = int(bet_index)
            bet_amount = int(bet_amount)
            assert 1 <= bet_index <= 4
        except Exception:
            await ctx.send(
                content="!gamble takes two arguments: which line to\
                    bet on and the bet amount"
            )
            return

        progress = [0, 0, 0, 0]
        emojis = [EMOJI_SUNGLASSES, EMOJI_HEART_EYES, EMOJI_THINKING, EMOJI_GRINNING]
        goal = 20

        race_embed = get_embed(
            "Horse Race",
            get_race_string(progress, emojis, goal),
            discord.Color.purple(),
        )
        message = await ctx.send(embed=race_embed)

        while max(progress) < goal:
            random_index = random.randint(0, len(progress) - 1)
            progress[random_index] += 1

            updated_message = race_embed.copy()
            updated_message.description = get_race_string(progress, emojis, goal)
            await message.edit(embed=updated_message)

            race_embed = updated_message
            time.sleep(0.1)

        author = ctx.author.name
        nr_tokens_won = get_gamble_result(progress, bet_index - 1, bet_amount)

        result_embed = get_embed(
            "Horse Race Results",
            f"{author} won {nr_tokens_won} token(s)!",
            discord.Color.gold(),
        )
        await ctx.send(embed=result_embed)

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

        embed_loading = get_embed(
            "Crossword Checker",
            "Checking if crossword is complete...",
            discord.Color.teal(),
        )
        message = await reaction.message.channel.send(embed=embed_loading)

        if not wapo_api.is_complete(puzzle_link):
            embed_error = get_embed(
                "Crossword Checker", "Crossword is not complete", discord.Color.red()
            )
            await message.edit(embed=embed_error)
            return

        puzzle_date = helper.get_puzzle_date(puzzle_link)

        if puzzle_date in self.solved:
            embed_warning = get_embed(
                "Crossword Checker",
                "Crossword is already solved",
                discord.Color.orange(),
            )
            await message.edit(embed=embed_warning)
            return

        self.solved.add(puzzle_date)

        puzzle_weekday = helper.get_puzzle_weekday(puzzle_date)
        puzzle_time = wapo_api.get_puzzle_time(puzzle_link)
        puzzle_reward = helper.get_puzzle_reward(puzzle_weekday, puzzle_time)

        for p in self.players:
            self.players[p] += puzzle_reward

        embed_success = get_embed(
            "Crossword Checker",
            f"Crossword complete! {puzzle_reward}x token(s) rewarded 🪙",
            discord.Color.green(),
        )

        await message.edit(embed=embed_success)


def get_embed(
    title: str, description: str, color: discord.Color, url: str = None
) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color, url=url)
    embed.set_footer(text=GITHUB_REPOSITORY, icon_url=GITHUB_ICON)
    return embed


def get_race_string(progress, emojis, goal) -> str:
    if len(progress) != len(emojis):
        raise Exception("Progress and emojis must be of the same size")

    if max(progress) > goal:
        raise Exception("Progress must be smaller than or equal to goal")

    lines = []
    lines.append("```")
    for i, line_progress in enumerate(progress):
        line = "#" * line_progress + emojis[i] + "." * (goal - line_progress)
        lines.append(line)
    lines.append("```")

    return "\n\n".join(lines)


def get_gamble_result(standings, bet_index, bet_amount) -> int:
    result = standings[bet_index]
    position = sorted(standings, reverse=True).index(result)

    winnings_table = {0: 2, 1: 1.5, 2: 0.5, 3: 0}
    return math.floor(winnings_table[position] * bet_amount)


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
