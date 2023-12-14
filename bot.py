import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

import wapo_api


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!')
CHANNEL_ID = 1184096292905943120


@bot.command()
async def wapo(ctx):
    if CHANNEL_ID == ctx.channel.id:
        message = await ctx.send('Fetching URL...')

        try:
            url = wapo_api.get_todays_wapo_url()
            await message.edit(content=url)
        except Exception:
            await ctx.send('Error fetching URL')


bot.run(os.getenv("DISCORD_TOKEN"))
