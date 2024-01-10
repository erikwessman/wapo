import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from db import DB
from cogs.crossword_cog import CrosswordCog
from cogs.admin_cog import AdminCog
from cogs.gamble_cog import GambleCog
from cogs.player_cog import PlayerCog
from cogs.store_cog import StoreCog
from cogs.stock_cog import StockCog
from cogs.reward_cog import RewardCog
from services.player_service import PlayerService
from services.crossword_service import CrosswordService
from services.roulette_service import RouletteService
from services.horse_race_service import HorseRaceService
from services.stock_service import StockService
from store import Store
from case_api import CaseAPI


class WaPoBot(commands.Bot):
    def __init__(self, db: DB, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.player_service = PlayerService(db)
        self.crossword_service = CrosswordService(db)
        self.roulette_service = RouletteService(db)
        self.horse_race_service = HorseRaceService(db)
        self.stock_service = StockService(db)
        self.store = Store("data/items.json")
        self.case_api = CaseAPI("data/cases.json")

    async def on_ready(self):
        print(f"{self.user} has connected!")
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    async def on_command_error(self, ctx, error):
        print(f"Error: {error}")

        if isinstance(error, commands.CommandNotFound):
            await ctx.send(content=error)
        elif isinstance(error, ValueError):
            await ctx.send(content="Internal error")


class WaPoHelp(commands.HelpCommand):
    """
    Helper class that prints a better !help command
    """

    def get_command_signature(self, command):
        return (
            f"{self.context.clean_prefix}{command.qualified_name} "
            f"{command.signature}"
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


async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True

    db = DB("wapo")
    bot = WaPoBot(db, command_prefix="!", intents=intents)
    bot.help_command = WaPoHelp()
    await bot.add_cog(CrosswordCog(bot))
    await bot.add_cog(GambleCog(bot))
    await bot.add_cog(PlayerCog(bot))
    await bot.add_cog(StoreCog(bot))
    await bot.add_cog(StockCog(bot))
    await bot.add_cog(RewardCog(bot))
    await bot.add_cog(AdminCog(bot))
    await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
