import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

from token_api import TokenAPI
from cogs.crossword import CrosswordCog
from cogs.tokens import TokenCog


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
