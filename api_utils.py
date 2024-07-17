import json
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
import pandas_market_calendars as mcal
from bcolors import bcolors
import alpaca.trading.enums as enums

# Load the .env file
load_dotenv()

# Define global variables for the API keys and secrets
FINANCIAL_MODELING_PREP_API_ENDPOINT = os.getenv(
    "FINANCIAL_MODELING_PREP_API_ENDPOINT")
FINANCIAL_MODELING_PREP_API_KEY = os.getenv("FINANCIAL_MODELING_PREP_API_KEY")

# Define the market calendar
nyse = mcal.get_calendar("NYSE")


def format_money(amount):
    amount = float(amount)
    return "-${0:,.2f}".format(amount) if amount < 0 else "${0:,.2f}".format(amount)


def format_percent(decimal):
    decimal = float(decimal)*100
    return "-{0:.2f}%".format(decimal) if decimal < 0 else "{0:.2f}%".format(decimal)


"""
Prints the position of the stock
:param position: The position of the stock

position = {
    asset_id,
    symbol, --> WHITE_FG
    exchange, --> BRIGHT_YELLOW_FG (NYSE), BRIGHT_CYAN_FG (NASDAQ), BRIGHT_RED_FG (TSX), BRIGHT_BLUE_FG (AMEX)
    asset_class, --> WHITE_FG
    asset_marginable, --> WHITE_FG (True), BRIGHT_BLACK_FG (False)
    avg_entry_price, --> WHITE_FG
    qty, --> WHITE_FG
    side, --> BRIGHT_GREEN_FG (long), BRIGHT_RED_FG (short)
    market_value, --> WHITE_FG
    cost_basis, --> WHITE_FG
    unrealized_pl, --> GREEN_FG (positive), RED_FG (negative)
    unrealized_plpc, --> GREEN_FG (positive), RED_FG (negative)
    unrealized_intraday_pl, --> GREEN_FG (positive), RED_FG (negative)
    unrealized_intraday_plpc, --> GREEN_FG (positive), RED_FG (negative)
    current_price, --> WHITE_FG
    lastday_price, --> WHITE_FG
    change_today, --> GREEN_FG (positive), RED_FG (negative)
    swap_rate,
    avg_entry_swap_rate,
    usd,
    qty_available --> WHITE_FG
    }

"""


def print_position(position):
    print(bcolors.BOLD + bcolors.BRIGHT_WHITE_FG + "Position" + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Symbol: " +
          bcolors.MAGENTA_FG + position.symbol + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Exchange: " + (bcolors.BRIGHT_YELLOW_FG if position.exchange == enums.AssetExchange.NYSE else (bcolors.BRIGHT_CYAN_FG if position.exchange ==
          enums.AssetExchange.NASDAQ else (bcolors.BRIGHT_BLUE_FG if position.exchange == enums.AssetExchange.AMEX else bcolors.BRIGHT_RED_FG))) + position.exchange + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Asset Class: " +
          bcolors.WHITE_FG + position.asset_class + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Asset Marginable: " +
          bcolors.WHITE_FG + str(position.asset_marginable) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Average Entry Price: " +
          bcolors.WHITE_FG + format_money(position.avg_entry_price) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Quantity: " +
          bcolors.WHITE_FG + str(position.qty) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Side: " + ((bcolors.BRIGHT_GREEN_FG if position.side ==
          enums.PositionSide.LONG else bcolors.BRIGHT_RED_FG) + position.side) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Market Value: " + bcolors.WHITE_FG +
          format_money(position.market_value) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Cost Basis: " + bcolors.WHITE_FG +
          format_money(position.cost_basis) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Unrealized P/L: " + ((bcolors.GREEN_FG + "+" if float(position.unrealized_pl)
          >= 0 else bcolors.RED_FG + "-")) + format_money(abs(float(position.unrealized_pl))) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Unrealized P/L Percentage: " + (bcolors.GREEN_FG + "+" if float(position.unrealized_plpc)
          >= 0 else bcolors.RED_FG + "-") + format_percent(abs(float(position.unrealized_plpc))) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Unrealized Intraday P/L: " + ((bcolors.GREEN_FG + "+" if float(position.unrealized_intraday_pl)
          >= 0 else bcolors.RED_FG + "-") + format_money(abs(float(position.unrealized_intraday_pl))) + bcolors.ENDC))
    print(bcolors.BRIGHT_WHITE_FG + "Unrealized Intraday P/L Percentage: " + (bcolors.GREEN_FG + "+" if float(position.unrealized_intraday_plpc)
          >= 0 else bcolors.RED_FG + "-") + format_percent(abs(float(position.unrealized_intraday_plpc))) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Current Price: " + bcolors.WHITE_FG +
          format_money(position.current_price) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Last Day Price: " +
          bcolors.WHITE_FG + format_money(position.lastday_price) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Change Today: " + ((bcolors.GREEN_FG if float(
        position.change_today) >= 0 else bcolors.RED_FG) + format_money(position.change_today)) + bcolors.ENDC)
    print(bcolors.BRIGHT_WHITE_FG + "Quantity Available: " +
          bcolors.WHITE_FG + str(position.qty_available) + bcolors.ENDC)


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
        "vwap": bar.vwap,
    }


def parse_response_into_tickers(response):
    return [stock["symbol"] for stock in response]


def get_stock_tickers():
    params = {
        "marketCapMoreThan": "1000000000",
        "exchange": "NYSE,NASDAQ,TSX,AMEX",
        "limit": "100",
        "apikey": FINANCIAL_MODELING_PREP_API_KEY,
    }
    response = requests.get(
        FINANCIAL_MODELING_PREP_API_ENDPOINT, params=params)  # type: ignore
    if not os.path.exists("output"):
        os.makedirs("output")
    with open("output/tickers.json", "w") as f:
        json.dump(response.json(), f, indent=4)
    with open("output/tickers.json", "r") as f:
        return json.load(f)


def get_stock_bars(client, tickers, start, end):
    stocks_req = StockBarsRequest(
        symbol_or_symbols=tickers, start=start, end=end, timeframe=TimeFrame.Minute  # type: ignore
    )
    print(f"Requesting stock bars from {
          start} to {end} for tickers: {tickers}")
    try:
        stocks_bars = client.get_stock_bars(stocks_req)
        print("Received stock bars:", stocks_bars)
        return stocks_bars
    except Exception as e:
        print(f"Error fetching stock bars: {e}")
        return None


def save_stock_bars_to_json(stocks_bars, tickers):
    bad_tickers = []
    if stocks_bars is None:
        print("No stock bars data received.")
        return bad_tickers

    for ticker in tickers:
        data = []
        if ticker not in stocks_bars.data:
            print("Ticker not found", ticker)
            bad_tickers.append(ticker)
            continue
        for bar in stocks_bars[ticker]:
            data.append(convert_Bar_to_dict(bar))
        if not os.path.exists(f"output/tickers/{ticker.lower()}"):
            os.makedirs(f"output/tickers/{ticker.lower()}")
        with open(f"output/tickers/{ticker.lower()}/{ticker.lower()}_bars.json", "w") as f:
            json.dump(data, f, indent=4)
    return [ticker for ticker in tickers if ticker not in bad_tickers]


def filter_tickers(tickers):
    return [ticker.replace("-", ".") for ticker in tickers]


def adjust_for_market_days(start, end):
    # Adjust the datetime if it's a weekend or holiday
    while nyse.valid_days(start.date(), end.date()).empty:
        start -= timedelta(days=1)
        end -= timedelta(days=1)
    return start, end
