import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import List
import yfinance as yf

from schemas.stock import Stock
from schemas.stock_price import StockPrice


class StockSim:
    def __init__(self):
        pass

    def simulate_initial_stock_prices(
        self, ticker: str, days_back: int = 30
    ) -> List[StockPrice]:
        start_date = datetime.now() - timedelta(days=days_back)
        end_date = datetime.now()

        historical_prices = self.fetch_historical_prices(ticker)
        return self.monte_carlo_simulation(historical_prices, start_date, end_date)

    def simulate_next_stock_price(self, stock_prices: pd.DataFrame) -> pd.DataFrame:
        start_date = stock_prices.index[-1]
        end_date = datetime.now()
        return self.monte_carlo_simulation(stock_prices, start_date, end_date)

    def stock_prices_to_dataframe(self, stock_prices: List[StockPrice]) -> pd.DataFrame:
        prices = [sp.price for sp in stock_prices]
        timestamps = [sp.timestamp for sp in stock_prices]

        return pd.DataFrame(prices, index=pd.to_datetime(timestamps), columns=["Price"])

    def dataframe_to_stock_prices(self, ticker, df) -> List[StockPrice]:
        stock_prices = []
        for timestamp, row in df.iterrows():
            stock_price = StockPrice(
                ticker=ticker, timestamp=timestamp, price=row["Price"]
            )
            stock_prices.append(stock_price)

        return stock_prices

    def fetch_historical_prices(self, ticker: str, days_back=90) -> pd.DataFrame:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        df = yf.download(ticker, start=start_date, end=end_date)

        if "Adj Close" not in df.columns:
            raise ValueError("Adjusted Close prices not available for this ticker.")

        if not isinstance(df.index, pd.DatetimeIndex):
            df["Date"] = pd.to_datetime(df.index)
            df.set_index("Date", inplace=True)

        df = df[["Adj Close"]].rename(columns={"Adj Close": "Price"})
        return df

    def monte_carlo_simulation(self, historical_data, start_date, end_date):
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)

        total_hours = (end_date - start_date).total_seconds() / 3600.0

        if total_hours < 1:
            return pd.DataFrame(columns=["Price"])

        date_range_start = start_date + pd.Timedelta(hours=1)
        date_range = pd.date_range(start=date_range_start, end=end_date, freq="H")

        # Replace zero or negative values with 1
        historical_data["Price"] = historical_data["Price"].apply(lambda x: 1 if x <= 0 else x)

        log_returns = np.log(1 + historical_data["Price"].pct_change())

        # Handling NaN values that may have been introduced
        log_returns = log_returns.fillna(0)

        mu = log_returns.mean()
        sigma = log_returns.std()

        # Simulate future hourly returns
        sim_rets = np.random.normal(mu, sigma, len(date_range))

        # Calculate simulated prices
        initial_price = historical_data["Price"].iloc[-1]
        sim_prices = initial_price * (sim_rets + 1).cumprod()

        sim_prices_df = pd.DataFrame(sim_prices, index=date_range, columns=["Price"])

        return sim_prices_df

    def plot_stock_prices(self, stock: Stock, stock_prices: List[StockPrice]):
        df = self.stock_prices_to_dataframe(stock_prices)

        fig, ax = plt.subplots(figsize=(10, 6))

        df["Price"].plot(ax=ax, color="teal", linewidth=2)

        ax.set_title(f"{stock.company} - ${stock.ticker}", fontsize=16)
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("Price", fontsize=14)

        ax.grid(True, linestyle="--", alpha=0.7)

        ax.tick_params(axis="x", labelsize=12, labelrotation=45)
        ax.tick_params(axis="y", labelsize=12)

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)

        plt.close(fig)
        return buffer
