import os
import time
import math
import random
import asyncio
import discord
from typing import List
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
        # TODO: Log stuff here

        print(error)

        if isinstance(error, commands.CommandNotFound):
            await ctx.send(content=error)


class TokenCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def send(self, ctx, user: discord.User, amount: int):
        author_id = ctx.author.id
        author_tokens = self.bot.token_api.get_tokens(author_id)

        if author_id == user.id:
            raise commands.BadArgument("Cannot send tokens to yourself")

        if amount < 1:
            raise commands.BadArgument("Cannot send less than 1 token")

        if author_tokens < amount:
            raise commands.BadArgument("Insufficient tokens")

        self.bot.token_api.update_tokens(author_id, -amount)
        self.bot.token_api.update_tokens(user.id, amount)

        await ctx.send(content=f"Gave {user.name} {amount} token(s)")

    @send.error
    async def send_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!send` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def register(self, ctx):
        author_id = ctx.author.id
        author_name = ctx.author.name

        if self.bot.token_api.has_player(author_id):
            raise commands.CommandError(f"{author_name} already registered")
        else:
            self.bot.token_api.set_tokens(author_id, 0)
            await ctx.send(content=f"Registered {author_name}")

    @register.error
    async def register_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!register` error: {error}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tokens(self, ctx):
        author_id = ctx.author.id
        author_tokens = self.bot.token_api.get_tokens(author_id)
        await ctx.send(content=f"You have {author_tokens} tokens")

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def gamble(self, ctx, row: int, amount: int):
        if not 1 <= row <= 4:
            raise commands.BadArgument("You must gamble on rows 1-4")

        if amount < 1:
            raise commands.BadArgument("You must gamble at least 1 token")

        author_id = ctx.author.id
        author_name = ctx.author.name
        author_tokens = self.bot.token_api.get_tokens(author_id)

        if author_tokens < amount:
            raise commands.CommandError("Insufficient tokens")

        self.bot.token_api.update_tokens(author_id, -amount)

        race_values = [0, 0, 0, 0]
        race_length = 20
        race_symbols = [EMOJI_ROCKET, EMOJI_PENGUIN, EMOJI_OCTOPUS, EMOJI_SANTA]

        race_embed = get_embed(
            "Horse Race",
            get_race_string(race_values, race_symbols, race_length),
            discord.Color.purple(),
        )
        race_message = await ctx.send(embed=race_embed)

        standings = await simulate_race(
            race_values, race_length, race_symbols, race_message, race_embed
        )

        nr_tokens_won = get_gamble_result(standings, row - 1, amount)
        self.bot.token_api.update_tokens(author_id, nr_tokens_won)

        result_embed = get_embed(
            "Horse Race Results",
            f"{author_name} won {nr_tokens_won} token(s)!",
            discord.Color.gold(),
        )
        await ctx.send(embed=result_embed)

    @gamble.error
    async def gamble_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content="`!gamble` error: Incorrect arguments")
        elif isinstance(error, commands.CommandError):
            await ctx.send(content=f"`!gamble` error: {error}")


class CrosswordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.solved = set()

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.default)
    async def wapo(self, ctx):
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
    async def wapo_error(self, ctx, error):
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


class WaPoHelp(commands.HelpCommand):
    def get_command_signature(self, command):
        return "%s%s %s" % (
            self.context.clean_prefix,
            command.qualified_name,
            command.signature,
        )

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", color=discord.Color.blurple())

        for cog, cmds in mapping.items():
            filtered = await self.filter_commands(cmds, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]

            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(
                    name=cog_name, value="\n".join(command_signatures), inline=False
                )

        channel = self.get_destination()
        await channel.send(embed=embed)


def get_embed(
    title: str, description: str, color: discord.Color, url: str = None
) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color, url=url)
    embed.set_footer(text=GITHUB_REPOSITORY, icon_url=GITHUB_ICON)
    return embed


async def simulate_race(
    race_values: List[int],
    race_length: int,
    race_symbols: List[str],
    race_message: discord.Message,
    race_embed: discord.Embed,
):
    reached_threshold_indices = []
    below_threshold = set(range(len(race_values)))

    while below_threshold:
        index = random.choice(list(below_threshold))
        race_values[index] += 1

        if race_values[index] >= race_length:
            below_threshold.remove(index)
            reached_threshold_indices.append(index)

        updated_message = race_embed.copy()
        updated_message.description = get_race_string(
            race_values, race_symbols, race_length
        )
        await race_message.edit(embed=updated_message)

        race_embed = updated_message
        time.sleep(0.1)

    return reached_threshold_indices


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


def get_gamble_result(standings: List[int], row: int, amount: int) -> int:
    bet_result_index = standings.index(row)
    winnings_table = {0: 2, 1: 1.5, 2: 0.5, 3: 0}
    return math.floor(winnings_table[bet_result_index] * amount)


async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True

    bot = WaPoBot(command_prefix="!", intents=intents)
    bot.help_command = WaPoHelp()
    await bot.add_cog(TokenCog(bot))
    await bot.add_cog(CrosswordCog(bot))
    await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
