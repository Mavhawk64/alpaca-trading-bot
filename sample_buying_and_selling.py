from paper_bot import place_dollar_share_orders
import json
from alpaca.trading.client import TradingClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from dotenv import load_dotenv
import os
# Load the .env file
load_dotenv()

# Define global variables for the API keys and secrets
ALPACA_PAPER_TOKEN = os.getenv("ALPACA_PAPER_TOKEN")
ALPACA_PAPER_SECRET = os.getenv("ALPACA_PAPER_SECRET")
ALPACA_LIVE_TOKEN = os.getenv("ALPACA_LIVE_TOKEN")
ALPACA_LIVE_SECRET = os.getenv("ALPACA_LIVE_SECRET")

trading_client = TradingClient(
    ALPACA_PAPER_TOKEN, ALPACA_PAPER_SECRET, paper=True)

shdc_client = StockHistoricalDataClient(
    ALPACA_PAPER_TOKEN, ALPACA_PAPER_SECRET)

with open("output/tickers.json", "r") as f:
    tickers = json.load(f)
tickers = tickers[:5]
tickers = [ticker["symbol"] for ticker in tickers]
print(tickers)

place_dollar_share_orders(
    client=trading_client, shdc_client=shdc_client, tickers=tickers, dollars_per_ticker=100)
