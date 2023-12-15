import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

import wapo_api
from const import CHANNEL_ID, GITHUB_REPOSITORY, GITHUB_ICON


load_dotenv()


# Allow one !wapo request at a time
is_generating_url = False

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
        if reaction.emoji == "👍" or reaction.emoji == "✅":
            # TODO
            # Get the puzzle link
            # Check that the puzzle is solved
            # Get the day and the time to solve
            pass


bot.run(os.getenv("DISCORD_TOKEN"))
