import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

from managers.crossword_manager import CrosswordManager
from managers.store_manager import StoreManager
from managers.player_manager import PlayerManager
from cogs.crossword_cog import CrosswordCog
from cogs.gamble_cog import GambleCog
from cogs.player_cog import PlayerCog
from cogs.store_cog import StoreCog


class WaPoBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.crossword_manager = CrosswordManager("data/crosswords.json")
        self.player_manager = PlayerManager("data/players.json")
        self.store_manager = StoreManager("data/items.json")

    async def on_ready(self):
        print(f"{self.user} has connected!")

    async def close(self):
        print("Bot is shutting down. Saving data...")
        self.crossword_manager.save_data()
        self.player_manager.save_data()
        self.store_manager.save_data()
        await super().close()

    async def on_command_error(self, ctx, error):
        # TODO: Log stuff here

        print(error)

        if isinstance(error, commands.CommandNotFound):
            await ctx.send(content=error)


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

    bot = WaPoBot(command_prefix="!", intents=intents)
    bot.help_command = WaPoHelp()
    await bot.add_cog(CrosswordCog(bot))
    await bot.add_cog(GambleCog(bot))
    await bot.add_cog(PlayerCog(bot))
    await bot.add_cog(StoreCog(bot))
    await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
