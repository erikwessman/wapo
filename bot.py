import os
from discord.ext import commands
from dotenv import load_dotenv

import wapo


load_dotenv()

bot = commands.Bot(command_prefix='!wapo')
channel_id = 1184096292905943120


@bot.command()
async def your_command(ctx):
    if channel_id == ctx.channel.id:
        message = await ctx.send('Fetching URL...')

        url = wapo.get_todays_wapo_url()

        await message.edit(content=url)


bot.run(os.getenv("DISCORD_TOKEN"))
