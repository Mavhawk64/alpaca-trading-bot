import json
from math import floor
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Optional
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from dotenv import load_dotenv

import api_utils

# Load the .env file
load_dotenv()

# Define global variables for the API keys and secrets
ALPACA_PAPER_TOKEN = os.getenv("ALPACA_PAPER_TOKEN")
ALPACA_PAPER_SECRET = os.getenv("ALPACA_PAPER_SECRET")
ALPACA_LIVE_TOKEN = os.getenv("ALPACA_LIVE_TOKEN")
ALPACA_LIVE_SECRET = os.getenv("ALPACA_LIVE_SECRET")


def place_market_orders(client: TradingClient, tickers: List[str]) -> None:
    market_reqs = [
        MarketOrderRequest(
            symbol=ticker, qty=1, side=OrderSide.BUY, time_in_force=TimeInForce.GTC
        )
        for ticker in tickers
    ]
    for req in market_reqs:
        client.submit_order(req)
        print("Order placed")


def place_dollar_share_orders(client: TradingClient, shdc_client: StockHistoricalDataClient, tickers: List[str], dollars_per_ticker: float) -> None:
    for ticker in tickers:
        # Get the current price of the stock
        price = api_utils.get_current_price(shdc_client, ticker)
        # convert price to 2 decimal places
        price = round(price, 2)
        # Calculate the number of shares to buy
        shares = dollars_per_ticker // price
        # Place the order
        client.submit_order(
            LimitOrderRequest(
                symbol=ticker, qty=floor(shares), side=OrderSide.BUY, time_in_force=TimeInForce.DAY, limit_price=price, extended_hours=True
            )
        )
        print(f"Order placed for {shares} shares of {ticker} at {price}")


def print_account_summary(client: TradingClient, pause: Optional[bool] = True) -> None:
    # Let's GET our account summary
    account = client.get_account()
    # Account summary consists of:
    # Portfolio's Value
    # Buying Power
    # Cash
    # List of Positions as JSON/dict

    portfolio_value = account.portfolio_value
    buying_power = account.buying_power
    cash = account.cash
    positions = client.get_all_positions()
    print("\n\n\n\n\n\n")
    for i in range(len(positions)):
        print(f"Portfolio Value:\t{api_utils.format_money(portfolio_value)}")
        print(f"Buying Power:\t\t{api_utils.format_money(buying_power)}")
        print(f"Cash:\t\t\t{api_utils.format_money(cash)}")
        print("\n\n")
        api_utils.print_position(positions[i])
        if pause:
            input("Press Enter to continue...")
        print("\n\n\n")


def main(place_orders: Optional[bool] = False, empty_output_dir: Optional[bool] = False, screen_stocks: Optional[bool] = False) -> None:
    if empty_output_dir:
        # rm -rf output
        shutil.rmtree("output", ignore_errors=True)

    trading_client = TradingClient(
        ALPACA_PAPER_TOKEN, ALPACA_PAPER_SECRET, paper=True)
    shdc_client = StockHistoricalDataClient(
        ALPACA_PAPER_TOKEN, ALPACA_PAPER_SECRET)

    # Get the stock tickers
    if screen_stocks:
        tickers_response = api_utils.get_stock_tickers()
        tickers = api_utils.parse_response_into_tickers(
            tickers_response, "volume")
        tickers = api_utils.filter_tickers(tickers)

        end = datetime.now()
        start = end - timedelta(minutes=100)
        start, end = api_utils.adjust_for_market_days(start, end)

        stocks_bars = api_utils.get_stock_bars(
            shdc_client, tickers, start, end)

        tickers = api_utils.save_stock_bars_to_json(stocks_bars, tickers)
        # print("Valid tickers after filtering and checking:", tickers)
    else:
        if not os.path.exists("output/tickers.json"):
            print("No output/tickers.json file found. Exiting.")
            with open("output/tickers.json", "r") as f:
                tickers = api_utils.parse_response_into_tickers(json.load(f))

    if place_orders:
        place_market_orders(trading_client, tickers)
    else:
        print("Order placement skipped.")

    # print_account_summary(trading_client, pause=False)


if __name__ == "__main__":
    place_orders = False  # Set this to True if you want to place orders
    empty_output_dir = (
        True  # Set this to True if you want to clear the output directory
    )
    screen_stocks = True  # Set this to True if you want to screen stocks

    main(place_orders, empty_output_dir, screen_stocks)
