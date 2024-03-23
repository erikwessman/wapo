import os
import asyncio
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv

from db import DB
from cogs.crossword_cog import CrosswordCog
from cogs.admin_cog import AdminCog
from cogs.gamble_cog import GambleCog
from cogs.roulette_cog import RouletteCog
from cogs.trivia_cog import TriviaCog
from cogs.player_cog import PlayerCog
from cogs.store_cog import StoreCog
from cogs.stock_cog import StockCog
from cogs.reward_cog import RewardCog
from cogs.duel_cog import DuelCog
from cogs.steal_cog import StealCog
from services.player_service import PlayerService
from services.crossword_service import CrosswordService
from services.roulette_service import RouletteService
from services.horse_race_service import HorseRaceService
from services.stock_service import StockService
from services.item_service import ItemService
from services.modifier_service import ModifierService
from classes.case_api import CaseAPI
from log import set_up_logger


class WaPoBot(commands.Bot):
    def __init__(self, db: DB, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.player_service = PlayerService(db)
        self.crossword_service = CrosswordService(db)
        self.roulette_service = RouletteService(db)
        self.horse_race_service = HorseRaceService(db)
        self.stock_service = StockService(db)
        self.item_service = ItemService(db, "data/items.json")
        self.modifier_service = ModifierService(db, "data/modifiers.json")
        self.case_api = CaseAPI("data/cases.json")

    async def on_ready(self):
        logging.info(f"{self.user} has connected!")
        try:
            synced = await self.tree.sync()
            logging.info(f"Synced {len(synced)} command(s)")
            logging.info("*** Bot is ready ***")
        except Exception as error:
            logging.error(error, exc_info=True)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            # These errors are handled at command-level, ignore
            pass
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(content=error)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(content=error)
        else:
            logging.error(error, exc_info=True)
            await ctx.send("Internal error. Command failed")


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
    await bot.add_cog(RouletteCog(bot))
    await bot.add_cog(TriviaCog(bot))
    await bot.add_cog(PlayerCog(bot))
    await bot.add_cog(StoreCog(bot))
    await bot.add_cog(StockCog(bot))
    await bot.add_cog(RewardCog(bot))
    await bot.add_cog(AdminCog(bot))
    await bot.add_cog(DuelCog(bot))
    await bot.add_cog(StealCog(bot))
    await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    load_dotenv()
    set_up_logger(True, "logs.txt")

    discord_token = os.getenv("DISCORD_TOKEN")
    if discord_token is None or discord_token.strip() == "":
        logging.error("DISCORD_TOKEN environment variable must be set")
        exit(1)

    asyncio.run(main())
