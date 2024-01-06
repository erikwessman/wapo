import discord
from datetime import datetime, timedelta
from discord.ext import commands, tasks

from helper import get_embed


class StockCog(commands.Cog):
    """
    Gathers commands relevant for stocks
    """

    def __init__(self, bot):
        self.bot = bot
        self.update_stock_price.start()

    @commands.hybrid_group(name="stock", description="Group of stock commands")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stock(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid stock command. Try !stock <subcommand>.")

    @stock.error
    async def stock_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(f"`stock` error: {error}")

    @stock.command(name="list")
    async def stock_list(self, ctx):
        stocks = self.bot.stock_service.get_all_stocks()

        embed = get_embed(
            "Stock List", "Here are the available stocks:", discord.Color.orange()
        )

        date_24_hrs = datetime.now() - timedelta(days=1)
        date_1_week = datetime.now() - timedelta(days=7)

        for stock in stocks:
            curr_price = self.bot.stock_service.get_current_stock_price(stock)
            price_24_hrs = self.bot.stock_service.get_stock_price_by_date(
                stock, date_24_hrs
            )
            price_1_week = self.bot.stock_service.get_stock_price_by_date(
                stock, date_1_week
            )

            change_24_hrs = (
                ((curr_price - price_24_hrs) / price_24_hrs) * 100
                if price_24_hrs
                else 0
            )
            change_1_week = (
                ((curr_price - price_1_week) / price_1_week) * 100
                if price_1_week
                else 0
            )

            emoji_24_hrs = "\U0001F4C8" if change_24_hrs >= 0 else "\U0001F4C9"
            emoji_1_week = "\U0001F4C8" if change_1_week >= 0 else "\U0001F4C9"

            field_value = (
                f"Current: {curr_price} "
                f"- 24h: {change_24_hrs:.2f}% {emoji_24_hrs} "
                f"- Week: {change_1_week:.2f}% {emoji_1_week}"
            )
            embed.add_field(
                name=f"{stock.company} - ${stock.ticker}",
                value=field_value,
                inline=False,
            )

        await ctx.send(embed=embed)

    @stock_list.error
    async def stock_list_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(f"`stock list` error: {error}")

    @stock.command(name="price")
    async def stock_price(self, ctx, ticker: str):
        stock = self.bot.stock_service.get_stock(ticker)
        price = self.bot.stock_service.get_current_stock_price(stock)
        await ctx.send(f"{ticker}: {price} coin(s)")

    @stock_price.error
    async def stock_price_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(f"`stock_price` error: {error}")

    @stock.command(name="history")
    async def stock_history(self, ctx, ticker: str, date_range: str = None):
        stock = self.bot.stock_service.get_stock(ticker)
        stock_prices = []
        date_ranges = {"day": 1, "week": 7, "month": 30}

        if date_range:
            if date_range in date_ranges:
                days = date_ranges[date_range]
                start_date = datetime.now() - timedelta(days=days)
                end_date = datetime.now()
                stock_prices = self.bot.stock_service.get_stock_price_in_date_range(
                    stock, start_date, end_date
                )
            else:
                raise commands.CommandError(
                    f"Available date ranges: {' '.join(date_ranges)}"
                )
        else:
            stock_prices = self.bot.stock_service.get_stock_prices(stock)

        stock_plot = self.bot.stock_service.get_stock_price_plot(stock, stock_prices)
        file = discord.File(fp=stock_plot, filename="stock_plot.png")

        embed = get_embed(f"${stock.ticker}", "", discord.Color.green())
        embed.set_image(url="attachment://stock_plot.png")

        await ctx.send(embed=embed, file=file)

    @stock_history.error
    async def stock_history_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(f"`stock history` error: {error}")

    @stock.command(name="buy")
    async def stock_buy(self, ctx: commands.Context, ticker: str, quantity: int):
        if quantity < 1:
            raise commands.CommandError("You must buy at least 1 share")

        stock = self.bot.stock_service.get_stock(ticker)
        player = self.bot.player_service.get_player(ctx.author.id)
        stock_price = self.bot.stock_service.get_current_stock_price(stock)
        total = stock_price * quantity

        self.bot.player_service.buy_stock(player, stock.ticker, stock_price, quantity)

        await ctx.send(f"Bought {quantity} shares of {ticker} for {total} coins")

    @stock_buy.error
    async def stock_buy_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(f"`stock buy` error: {error}")

    @stock.command(name="sell")
    async def stock_sell(self, ctx: commands.Context, ticker: str, quantity: int):
        if quantity < 1:
            raise commands.CommandError("You must sell at least 1 share")

        stock = self.bot.stock_service.get_stock(ticker)
        player = self.bot.player_service.get_player(ctx.author.id)
        stock_price = self.bot.stock_service.get_current_stock_price(stock.ticker)
        total = stock_price * quantity

        self.bot.player_service.sell_stock(player, stock.ticker, stock_price, quantity)

        await ctx.send(f"Sold {quantity} shares of {ticker} for {total} coins")

    @stock_sell.error
    async def stock_sell_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(f"`stock sell` error: {error}")

    @tasks.loop(hours=1)
    async def update_stock_price(self):
        stocks = self.bot.stock_service.get_all_stocks()

        for stock in stocks:
            print(f"Updating {stock.company} stock prices...")
            self.bot.stock_service.simulate_next_stock_prices(stock)

    @update_stock_price.error
    async def update_stock_price_error(self, ctx, error):
        print(f"Error when updating stocks: {error}")

    @update_stock_price.before_loop
    async def before_my_background_task(self):
        await self.bot.wait_until_ready()
