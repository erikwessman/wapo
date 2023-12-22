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
from token_api import TokenAPI
from const import (
    CHANNEL_ID,
    GITHUB_REPOSITORY,
    GITHUB_ICON,
    EMOJI_ROCKET,
    EMOJI_PENGUIN,
    EMOJI_OCTOPUS,
    EMOJI_SANTA,
)


class WaPoBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.token_api = TokenAPI("data/tokens.json")

    async def on_ready(self):
        print(f"{self.user} has connected!")

    async def on_command_error(self, ctx, error):
        print(f"Command error: {error}")


class TokenCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def register(self, ctx):
        author_id = str(ctx.author.id)
        author_name = ctx.author.name

        if self.bot.token_api.has_player(author_id):
            await ctx.send(content=f"{author_name} already registered")
        else:
            self.bot.token_api.set_tokens(author_id, 0)
            await ctx.send(content=f"Registered {author_name}")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tokens(self, ctx):
        author_id = str(ctx.author.id)
        author_tokens = self.bot.token_api.get_tokens(author_id)
        await ctx.send(content=f"You have {author_tokens} tokens")

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def gamble(self, ctx, bet_index, bet_amount):
        try:
            bet_index = int(bet_index)
            bet_amount = int(bet_amount)
        except Exception:
            await ctx.send(
                content="!gamble takes two arguments: which line to\
                    bet on and the bet amount"
            )
            return

        if not 1 <= bet_index <= 4:
            await ctx.send(content="You must gamble on lines 1-4")
            return

        if bet_amount < 1:
            await ctx.send(content="You must gamble at least 1 token")
            return

        author_id = str(ctx.author.id)
        author_name = ctx.author.name
        author_tokens = self.bot.token_api.get_tokens(author_id)

        if author_tokens < bet_amount:
            await ctx.send(content="Not enough tokens")
            return

        progress = [0, 0, 0, 0]
        race_length = 20
        symbols = [EMOJI_ROCKET, EMOJI_PENGUIN, EMOJI_OCTOPUS, EMOJI_SANTA]

        race_embed = get_embed(
            "Horse Race",
            get_race_string(progress, symbols, race_length),
            discord.Color.purple(),
        )
        message = await ctx.send(embed=race_embed)

        while max(progress) < race_length:
            random_index = random.randint(0, len(progress) - 1)
            progress[random_index] += 1

            updated_message = race_embed.copy()
            updated_message.description = get_race_string(
                progress, symbols, race_length
            )
            await message.edit(embed=updated_message)

            race_embed = updated_message
            time.sleep(0.1)

        nr_tokens_won = get_gamble_result(progress, bet_index - 1, bet_amount)

        self.bot.token_api.update_tokens(author_id, nr_tokens_won)

        result_embed = get_embed(
            "Horse Race Results",
            f"{author_name} won {nr_tokens_won} token(s)!",
            discord.Color.gold(),
        )
        await ctx.send(embed=result_embed)


class CrosswordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.solved = set()

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.server)
    async def wapo(self, ctx):
        if CHANNEL_ID == ctx.channel.id and not self.is_generating_url:
            embed_loading = get_embed(
                "Washington Post Daily Crossword",
                "Fetching URL...",
                discord.Color.teal(),
            )
            message = await ctx.send(embed=embed_loading)

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
                await message.edit(embed=embed_success)

            except Exception as e:
                embed_error = get_embed(
                    "Washington Post Daily Crossword",
                    "Error fetching URL",
                    discord.Color.red(),
                )
                await message.edit(embed=embed_error)

                print(f"Unable to get URL: {e}")

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

        players = self.bot.token_api.get_players()

        for player in players:
            self.bot.token_api.update_tokens(player, puzzle_reward)

        embed_success = get_embed(
            "Crossword Checker",
            f"Crossword complete! {puzzle_reward} token(s) \
                   rewarded to {len(players)} players",
            discord.Color.green(),
        )

        await message.edit(embed=embed_success)


def get_embed(
    title: str, description: str, color: discord.Color, url: str = None
) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color, url=url)
    embed.set_footer(text=GITHUB_REPOSITORY, icon_url=GITHUB_ICON)

    return embed


def get_race_string(progress, symbols, race_length) -> str:
    if len(progress) != len(symbols):
        raise Exception("Progress and symbols must have the same length")

    if max(progress) > race_length:
        raise Exception("Progress must be less than or equal to goal")

    lines = []
    lines.append("```")
    for i, line_prog in enumerate(progress):
        line = "#" * line_prog + symbols[i] + "." * (race_length - line_prog)
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
    await bot.add_cog(TokenCog(bot))
    await bot.add_cog(CrosswordCog(bot))
    await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
