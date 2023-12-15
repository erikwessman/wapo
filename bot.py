import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

import wapo_api


load_dotenv()

# Wapo channel
CHANNEL_ID = 1184096292905943120

# Allow one !wapo request at a time
is_generating_url = False

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!')


@bot.command()
async def wapo(ctx):
    global is_generating_url

    if CHANNEL_ID == ctx.channel.id and not is_generating_url:
        embed_loading = discord.Embed(
                title="Washington Post Daily Crossword",
                description="Fetching URL...",
                color=discord.Color.teal()
        )
        message = await ctx.send(embed=embed_loading)

        try:
            is_generating_url = True
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

        finally:
            is_generating_url = False


bot.run(os.getenv("DISCORD_TOKEN"))
