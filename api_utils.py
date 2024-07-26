import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union

import alpaca.trading.enums as enums
import pandas_market_calendars as mcal
import requests
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.models import Bar, BarSet, RawData
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.models import Position
from dotenv import load_dotenv

from bcolors import bcolors

# Load the .env file
load_dotenv()

# Define global variables for the API keys and secrets
FINANCIAL_MODELING_PREP_API_ENDPOINT = os.getenv(
    "FINANCIAL_MODELING_PREP_API_ENDPOINT")
FINANCIAL_MODELING_PREP_API_KEY = os.getenv("FINANCIAL_MODELING_PREP_API_KEY")

# Define the market calendar
nyse = mcal.get_calendar("NYSE")


def format_money(amount: float) -> str:
    amount = float(amount)
    return "-${0:,.2f}".format(amount) if amount < 0 else "${0:,.2f}".format(amount)


def format_percent(decimal: float) -> str:
    decimal = float(decimal) * 100
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


def print_position(position: Position) -> None:
    print(bcolors.BOLD + bcolors.BRIGHT_WHITE_FG + "Position" + bcolors.ENDC)
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Symbol: "
        + bcolors.MAGENTA_FG
        + position.symbol
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Exchange: "
        + (
            bcolors.BRIGHT_YELLOW_FG
            if position.exchange == enums.AssetExchange.NYSE
            else (
                bcolors.BRIGHT_CYAN_FG
                if position.exchange == enums.AssetExchange.NASDAQ
                else (
                    bcolors.BRIGHT_BLUE_FG
                    if position.exchange == enums.AssetExchange.AMEX
                    else bcolors.BRIGHT_RED_FG
                )
            )
        )
        + position.exchange
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Asset Class: "
        + bcolors.WHITE_FG
        + position.asset_class
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Asset Marginable: "
        + bcolors.WHITE_FG
        + str(position.asset_marginable)
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Average Entry Price: "
        + bcolors.WHITE_FG
        + format_money(position.avg_entry_price)
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Quantity: "
        + bcolors.WHITE_FG
        + str(position.qty)
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Side: "
        + (
            (
                bcolors.BRIGHT_GREEN_FG
                if position.side == enums.PositionSide.LONG
                else bcolors.BRIGHT_RED_FG
            )
            + position.side
        )
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Market Value: "
        + bcolors.WHITE_FG
        + format_money(position.market_value)
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Cost Basis: "
        + bcolors.WHITE_FG
        + format_money(position.cost_basis)
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Unrealized P/L: "
        + (
            (
                bcolors.GREEN_FG + "+"
                if float(position.unrealized_pl) >= 0
                else bcolors.RED_FG + "-"
            )
        )
        + format_money(abs(float(position.unrealized_pl)))
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Unrealized P/L Percentage: "
        + (
            bcolors.GREEN_FG + "+"
            if float(position.unrealized_plpc) >= 0
            else bcolors.RED_FG + "-"
        )
        + format_percent(abs(float(position.unrealized_plpc)))
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Unrealized Intraday P/L: "
        + (
            (
                bcolors.GREEN_FG + "+"
                if float(position.unrealized_intraday_pl) >= 0
                else bcolors.RED_FG + "-"
            )
            + format_money(abs(float(position.unrealized_intraday_pl)))
            + bcolors.ENDC
        )
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Unrealized Intraday P/L Percentage: "
        + (
            bcolors.GREEN_FG + "+"
            if float(position.unrealized_intraday_plpc) >= 0
            else bcolors.RED_FG + "-"
        )
        + format_percent(abs(float(position.unrealized_intraday_plpc)))
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Current Price: "
        + bcolors.WHITE_FG
        + format_money(position.current_price)
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Last Day Price: "
        + bcolors.WHITE_FG
        + format_money(position.lastday_price)
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Change Today: "
        + (
            (bcolors.GREEN_FG if float(position.change_today) >= 0 else bcolors.RED_FG)
            + format_money(position.change_today)
        )
        + bcolors.ENDC
    )
    print(
        bcolors.BRIGHT_WHITE_FG
        + "Quantity Available: "
        + bcolors.WHITE_FG
        + str(position.qty_available)
        + bcolors.ENDC
    )


def convert_Bar_to_dict(bar: Bar) -> dict:
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


def parse_response_into_tickers(
    response: List[dict], order_by: Optional[str] = "volume"
) -> List[str]:
    response = sorted(response, key=lambda x: x[order_by], reverse=True)
    return [stock["symbol"] for stock in response]


def get_stock_tickers(order_by: Optional[str] = "volume") -> List[dict]:
    params = {
        "marketCapLowerThan": "3500000000",  # 3.5 billion
        "priceMoreThan": "1",
        "priceLowerThan": "20",
        "volumeMoreThan": "1000",
        "exchange": "NYSE,NASDAQ,TSX,AMEX",
        "limit": "6000",
        "isActivelyTrading": "true",
        "apikey": FINANCIAL_MODELING_PREP_API_KEY,
    }
    response = requests.get(
        FINANCIAL_MODELING_PREP_API_ENDPOINT, params=params, timeout=10
    )  # type: ignore

    response = response.json()
    # order by
    response = sorted(response, key=lambda x: x[order_by], reverse=True)

    if not os.path.exists("output"):
        os.makedirs("output")
    with open("output/tickers.json", "w") as f:
        json.dump(response, f, indent=4)
    with open("output/tickers.json", "r") as f:
        return json.load(f)


def get_stock_bars(
    client: StockHistoricalDataClient,
    tickers: List[str],
    start: datetime,
    end: datetime,
) -> Union[BarSet, RawData] | None:
    stocks_req = StockBarsRequest(
        symbol_or_symbols=tickers, start=start, end=end, timeframe=TimeFrame.Minute  # type: ignore
    )
    print(f"Requesting stock bars from {start} to {end}.")
    try:
        stocks_bars = client.get_stock_bars(stocks_req)
        return stocks_bars
    except Exception as e:
        print(f"Error fetching stock bars: {e}")
        return None


def save_stock_bars_to_json(
    stocks_bars: Union[BarSet, RawData, None], tickers: List[str]
) -> List[str]:
    bad_tickers = []
    if stocks_bars is None:
        print("No stock bars data received.")
        return bad_tickers

    for ticker in tickers:
        data = []
        if ticker not in stocks_bars.data:
            print(f"{bcolors.FAIL}Ticker not found", ticker, bcolors.ENDC)
            bad_tickers.append(ticker)
            continue
        print(f"{bcolors.OKCYAN}Saving {ticker} bars to JSON.{bcolors.ENDC}")
        for bar in stocks_bars[ticker]:
            data.append(convert_Bar_to_dict(bar))
        if not os.path.exists(f"output/tickers/{ticker.lower()}"):
            os.makedirs(f"output/tickers/{ticker.lower()}")
        with open(
            f"output/tickers/{ticker.lower()}/{ticker.lower()}_bars.json", "w"
        ) as f:
            json.dump(data, f, indent=4)
    return [ticker for ticker in tickers if ticker not in bad_tickers]


def filter_tickers(tickers: List[str]) -> List[str]:
    # return [ticker.replace("-", ".") for ticker in tickers]
    return [ticker for ticker in tickers if "-" not in ticker and "." not in ticker]


def adjust_for_market_days(start: datetime, end: datetime) -> Tuple[datetime, datetime]:
    # Adjust the datetime if it's a weekend or holiday
    while nyse.valid_days(start.date(), end.date()).empty:
        start -= timedelta(days=1)
        end -= timedelta(days=1)
    return start, end


def get_current_price(sdhc_client: StockHistoricalDataClient, ticker: str) -> float:
    bar = sdhc_client.get_stock_bars(
        StockBarsRequest(
            symbol_or_symbols=[ticker],
            start=datetime.now() - timedelta(days=1),
            end=datetime.now(),
            timeframe=TimeFrame.Minute,
        )
    )
    return bar[ticker][-1].close if bar is not None else 0.0
