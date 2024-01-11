import discord


class CustomView(discord.ui.View):
    """Custom discord View"""

    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.message = None

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        if self.message:
            await self.message.edit(view=self)
