import discord
from discord.ext import commands

import helper


class StoreCog(commands.Cog):
    """
    Gathers commands relevant for interacting with the store
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="store", description="View the item store")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def store(self, ctx: commands.Context):
        items = self.bot.item_service.get_purchasable_items()
        modifiers = self.bot.modifier_service.get_purchasable_modifiers()

        embed = helper.get_embed("Store", "Buy cool stuff", discord.Color.pink())

        embed.add_field(
            name="---Items---",
            value="Items appear in your inventory and can be used",
            inline=False,
        )

        for item in items:
            item_details = (
                f"**Description:** {item.description}\n"
                f"**Price:** {item.price} coins\n"
                f"**One Time Use:** {'Yes' if item.one_time_use else 'No'}"
            )
            embed.add_field(
                name=f"{item.name} {item.symbol}",
                value=item_details,
                inline=False,
            )

        embed.add_field(
            name="---Modifiers---",
            value="Modifiers are applied immediately",
            inline=False,
        )

        for modifier in modifiers:
            modifier_details = (
                f"**Description:** {modifier.description}\n"
                f"**Price:** {modifier.price} coins\n"
                f"**Stacking:** {'Yes' if modifier.is_stacking else 'No'}\n"
                f"**Timed:** {'Yes' if modifier.is_timed else 'No'}\n"
                f"**Duration:** {modifier.duration} hours\n"
                f"**Max stacks:** {modifier.max_stacks}x"
            )
            embed.add_field(
                name=f"{modifier.name} {modifier.symbol}",
                value=modifier_details,
                inline=False,
            )

        await ctx.send(embed=embed, ephemeral=True)

    @store.error
    async def store_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`store` error: {error}")

    @commands.hybrid_command(name="", description="")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cases(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        four_leaf_clover_modifier = self.bot.modifier_service.get_modifier("four_leaf_clover")
        has_clover = player.is_modifier_valid(four_leaf_clover_modifier)
        tiers = self.bot.case_api.get_tiers(has_clover)

        embed = helper.get_embed("Case Odds & Items", "", discord.Color.red())

        for tier, tier_info in tiers.items():
            items_string = " ".join(tier_info["items"])
            embed.add_field(
                name=f"{tier} - {tier_info['drop_rate']}%",
                value=f"```{items_string}```",
                inline=False,
            )

        await ctx.send(embed=embed)

    @cases.error
    async def cases_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`cases` error: {error}")

    @commands.hybrid_command(name="buy", description="Buy an item or modifier from the store")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def buy(self, ctx: commands.Context, item_name: str, quantity: int = 1):
        if quantity < 1:
            raise commands.BadArgument("Must buy at least 1 item")

        items = self.bot.item_service.get_purchasable_items()
        modifiers = self.bot.modifier_service.get_purchasable_modifiers()

        # Look at both items and modifiers and get the closest match
        item_names = [i.name for i in items]
        modifier_names = [m.name for m in modifiers]
        product_name = helper.closest_match(item_name, item_names + modifier_names)

        player = self.bot.player_service.get_player(ctx.author.id)

        if product_name in item_names:
            # Product is an item
            item = self.bot.item_service.get_item_by_name(product_name, False)

            if player.get_coins() < item.price * quantity:
                raise commands.BadArgument(
                    f"Not enough coins to buy {quantity}x {item.name}"
                )

            player.add_item(item.id, quantity)
            player.remove_coins(item.price * quantity)
            await ctx.send(content=f"Bought {quantity} {item.name}(s)", ephemeral=True)
        else:
            # Product is a modifier
            modifier = self.bot.modifier_service.get_modifier_by_name(product_name, False)

            # You should not be able to buy a timed modifier if you have one active
            player_modifier = player.get_modifier(modifier.id)
            if modifier.is_timed and not helper.has_hours_passed_since(player_modifier.last_used, modifier.duration):
                time_left = helper.calculate_time_left(player_modifier.last_used, modifier.duration)
                raise commands.BadArgument(f"Can't buy another {modifier.name} {modifier.symbol} [{time_left}] because you have one that is still active")

            # You should not be able to buy more than the max stacks
            if modifier.is_stacking and player.get_modifier_stacks(modifier.id) + quantity > modifier.max_stacks:
                stacks_string = player.get_modifier_stacks_string(modifier)
                raise commands.BadArgument(f"Can't buy that many stacks for {modifier.name} {stacks_string}")

            if player.get_coins() < modifier.price * quantity:
                raise commands.BadArgument(f"Not enough coins to buy {quantity}x {modifier.name}")

            player.add_modifier(modifier.id, quantity)
            player.remove_coins(modifier.price * quantity)
            await ctx.send(content=f"Bought {quantity} {modifier.name}(s)", ephemeral=True)

    @buy.error
    async def buy_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`buy` error: {error}")
