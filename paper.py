import json
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.client import TradingClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import pandas as pd
import requests

api_url = "https://financialmodelingprep.com/api/v3/stock-screener"

# Set up the parameters dictionary


# Load the .env file
load_dotenv()

# Get the environment variables
API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
EOD_KEY = os.getenv('EOD_KEY')
FMP_KEY = os.getenv('FMP_KEY')


def convert_Bar_to_dict(bar):
    return {
        "symbol": bar.symbol,
        "timestamp": bar.timestamp.isoformat(),
        "open": bar.open,
        "high": bar.high,
        "low": bar.low,
        "close": bar.close,
        "volume": bar.volume,
        "trade_count": bar.trade_count,
        "vwap": bar.vwap
    }


def parse_response_into_tickers(s):
    t = []
    for stock in s:
        t.append(stock["symbol"])
    return t


# OFFICIAL
# params = {
#     "marketCapMoreThan": "1000000000",
#     "exchange": "NYSE,NASDAQ,TSX,AMEX",
#     "limit": "100",
#     "apikey": FMP_KEY
# }

# response = requests.get(api_url, params=params)
# # output to outpu/tickers.json
# with open('output/tickers.json', 'w') as f:
#     json.dump(response.json(), f, indent=4)

# TESTING
response = ""
with open('output/tickers.json', 'r') as f:
    response = json.load(f)

print(parse_response_into_tickers(response))


# could get a list of tickers from blue book
tickers = parse_response_into_tickers(response)

# Importing the API and instantiating the REST client according to our keys


trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
shdc_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

# Getting account information and printing it
account = trading_client.get_account()
# print(type(account))

# Get the last 100 bars of stock at 1 minute intervals
start = datetime.now() - timedelta(minutes=100)
end = datetime.now()
stocks_req = StockBarsRequest(symbol_or_symbols=tickers, start=start,
                              end=end, timeframe=TimeFrame.Minute, adjustment=None, feed=None)

stocks_bars = shdc_client.get_stock_bars(stocks_req)
bad_tickers = []
for ticker in tickers:
    data = []
    if ticker not in stocks_bars.data:
        print("Ticker not found", ticker)
        bad_tickers.append(ticker)
        continue
    for bar in stocks_bars[ticker]:
        data.append(convert_Bar_to_dict(bar))
    # convert data (dict array) to json and save to output/aapl_bars.json with indent=4
    with open(f'output/{ticker.lower()}_bars.json', 'w') as f:
        json.dump(data, f, indent=4)

tickers = [ticker for ticker in tickers if ticker not in bad_tickers]
print(tickers)
# Setting parameters for our buy order

market_reqs = []

for ticker in tickers:
    market_order_data = MarketOrderRequest(
        symbol=ticker,
        qty=1,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.GTC
    )
    market_reqs.append(market_order_data)

# Placing the order
for i in market_reqs:
    trading_client.submit_order(i)
    print("Order placed")
