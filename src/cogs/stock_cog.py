import logging
from datetime import datetime, timedelta
import discord
from discord.ext import commands, tasks

import helper


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
            await ctx.send("Invalid stock command")

    @stock.error
    async def stock_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"`stock` error: {error}")

    @stock.command(name="list")
    async def stock_list(self, ctx):
        stocks = self.bot.stock_service.get_all_stocks()

        embed = helper.get_embed(
            "Stock List", "Here are the available stocks:", discord.Color.orange()
        )

        date_24_hrs = datetime.now() - timedelta(days=1)
        date_1_week = datetime.now() - timedelta(days=7)

        for stock in stocks:
            curr_price = self.bot.stock_service.get_current_stock_price(stock.ticker)
            price_24_hrs = self.bot.stock_service.get_stock_price_by_date(
                stock.ticker, date_24_hrs
            )
            price_1_week = self.bot.stock_service.get_stock_price_by_date(
                stock.ticker, date_1_week
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
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"`stock list` error: {error}")

    @stock.command(name="price")
    async def stock_price(self, ctx, ticker: str):
        if not self.bot.stock_service.has_stock(ticker):
            raise commands.BadArgument(f"Stock with ticker {ticker} does not exist")
        price = self.bot.stock_service.get_current_stock_price(ticker)
        await ctx.send(f"{ticker}: {price} coin(s)")

    @stock_price.error
    async def stock_price_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
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
                    stock.ticker, start_date, end_date
                )
            else:
                raise commands.BadArgument(
                    f"Available date ranges: {', '.join(date_ranges)}"
                )
        else:
            stock_prices = self.bot.stock_service.get_stock_prices(stock.ticker)

        stock_plot = self.bot.stock_service.get_stock_price_plot(stock, stock_prices)
        file = discord.File(fp=stock_plot, filename="stock_plot.png")

        embed = helper.get_embed(f"${stock.ticker}", "", discord.Color.green())
        embed.set_image(url="attachment://stock_plot.png")

        await ctx.send(embed=embed, file=file)

    @stock_history.error
    async def stock_history_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"`stock history` error: {error}")

    @stock.command(name="buy")
    async def stock_buy(self, ctx: commands.Context, ticker: str, quantity: int):
        player = self.bot.player_service.get_player(ctx.author.id)

        if not self.bot.stock_service.has_stock(ticker):
            raise commands.BadArgument(f"Stock with ticker {ticker} does not exist")

        stock_price = self.bot.stock_service.get_current_stock_price(ticker)
        total_cost = stock_price * quantity

        if quantity < 1:
            raise commands.BadArgument("Must buy at least one share")

        if stock_price < 1:
            raise commands.BadArgument("Can't buy a stock for less than 1 coin")

        if player.get_coins() < total_cost:
            raise commands.BadArgument(f"Not enough coins to buy {quantity}x ${ticker}")

        player.add_holding(ticker, quantity, stock_price)
        player.remove_coins(total_cost)

        await ctx.send(f"Bought {quantity} shares of {ticker} for {total_cost} coins")

    @stock_buy.error
    async def stock_buy_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"`stock buy` error: {error}")

    @stock.command(name="sell")
    async def stock_sell(self, ctx: commands.Context, ticker: str, quantity: int):
        player = self.bot.player_service.get_player(ctx.author.id)

        if not self.bot.stock_service.has_stock(ticker):
            raise commands.BadArgument(f"Stock with ticker {ticker} does not exist")

        stock_price = self.bot.stock_service.get_current_stock_price(ticker)
        total_cost = stock_price * quantity

        if quantity < 1:
            raise commands.BadArgument("Must sell at least one share")

        if stock_price < 1:
            raise commands.BadArgument("Can't sell a stock for less than 1 coin")

        if not player.has_holding(ticker):
            raise commands.BadArgument(f"You do not own any shares of ${ticker}")

        if player.get_holding(ticker).shares < quantity:
            raise commands.BadArgument("Not enough shares")

        player.remove_holding(ticker, quantity)
        player.add_coins(total_cost)

        await ctx.send(f"Sold {quantity} shares of {ticker} for {total_cost} coins")

    @stock_sell.error
    async def stock_sell_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"`stock sell` error: {error}")

    @tasks.loop(hours=1)
    async def update_stock_price(self):
        stocks = self.bot.stock_service.get_all_stocks()

        for stock in stocks:
            logging.debug("Updating %s stock prices...", stock.ticker)
            self.bot.stock_service.simulate_next_stock_prices(stock)

    @update_stock_price.before_loop
    async def before_update_stock_price(self):
        await self.bot.wait_until_ready()
