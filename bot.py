import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

import wapo_api


load_dotenv()

# Wapo channel
CHANNEL_ID = 1184096292905943120

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!')


@bot.command()
async def wapo(ctx):
    if CHANNEL_ID == ctx.channel.id:
        embed_loading = discord.Embed(
                title="Washington Post Daily Crossword",
                description="Fetching URL...",
                color=discord.Color.teal()
        )
        message = await ctx.send(embed=embed_loading)

        try:
            url = wapo_api.get_todays_wapo_url()

            embed_success = discord.Embed(
                    title="Washington Post Daily Crossword",
                    url=url,
                    description="URL generated!",
                    color=discord.Color.green()
            )

            await message.edit(embed=embed_success)

        except Exception:
            embed_error = discord.Embed(
                    title="Washington Post Daily Crossword",
                    description="Error fetching URL",
                    color=discord.Color.red()
            )
            await message.edit(embed=embed_error)


bot.run(os.getenv("DISCORD_TOKEN"))
