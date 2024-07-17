import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import talib as ta
from datetime import datetime
from matplotlib.dates import date2num
from mpl_finance import _candlestick

# Load the JSON data
ticker = "AAPL"
data = json.load(
    open(f"./output/tickers/{ticker.lower()}/{ticker.lower()}_bars.json"))

# Extract data into a DataFrame
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# Prepare data for candlestick chart
df_ochl = df[['open', 'close', 'high', 'low']].copy()
df_ochl['date_num'] = date2num(df_ochl.index.to_pydatetime())
df_ochl = df_ochl[['date_num', 'open', 'close', 'high', 'low']]

# Technical Analysis Parameters
SMA_FAST = 50
SMA_SLOW = 200
RSI_PERIOD = 14
RSI_AVG_PERIOD = 15
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
STOCH_K = 14
STOCH_D = 3
Y_AXIS_SIZE = 12

# Technical Analysis Calculations
analysis = pd.DataFrame(index=df.index)
analysis['sma_f'] = df['close'].rolling(window=SMA_FAST).mean()
analysis['sma_s'] = df['close'].rolling(window=SMA_SLOW).mean()
analysis['rsi'] = ta.RSI(df['close'].values, timeperiod=RSI_PERIOD)
analysis['sma_r'] = analysis['rsi'].rolling(window=RSI_AVG_PERIOD).mean()
analysis['macd'], analysis['macdSignal'], analysis['macdHist'] = ta.MACD(
    df['close'].values, fastperiod=MACD_FAST, slowperiod=MACD_SLOW, signalperiod=MACD_SIGNAL)
analysis['stoch_k'], analysis['stoch_d'] = ta.STOCH(
    df['high'].values, df['low'].values, df['close'].values, slowk_period=STOCH_K, slowd_period=STOCH_D)

# Calculate the derivative of the MACD Histogram
analysis['macdHistDeriv'] = np.gradient(analysis['macdHist'])
# Calculate the second derivative of the MACD Histogram
analysis['macdHistDeriv2'] = np.gradient(analysis['macdHistDeriv'])

# if macdHistDeriv > 0 -> 1, macdHistDeriv < 0 -> -1, else 0
analysis['macdHistDeriv'] = np.sign(analysis['macdHistDeriv'])

# if macdHistDeriv2 > 0 -> 1, macdHistDeriv2 < 0 -> -1, else 0
analysis['macdHistDeriv2'] = np.sign(analysis['macdHistDeriv2'])

# Plot the macd on 2 charts (macd and signal ; macd histogram), also, find the derivative of the macdHist
fig, ax = plt.subplots(4, figsize=(15, 10))
ax[0].plot(analysis.index, analysis['macd'], label='MACD')
ax[0].plot(analysis.index, analysis['macdSignal'], label='Signal Line')
ax[0].set_title('MACD and Signal Line')
ax[0].set_ylabel('MACD')
ax[0].legend(loc='upper left')
ax[0].grid()
ax[1].plot(analysis.index, analysis['macdHist'], label='MACD Histogram')
ax[1].set_title('MACD Histogram')
ax[1].set_ylabel('MACD Hist')
ax[1].legend(loc='upper left')
ax[1].grid()
ax[2].plot(analysis.index, analysis['macdHistDeriv'],
           label='MACD Histogram Derivative')
ax[2].set_title('MACD Histogram Derivative')
ax[2].set_ylabel('MACD Hist Deriv')
ax[2].legend(loc='upper left')
ax[2].grid()
ax[3].plot(analysis.index, analysis['macdHistDeriv2'],
           label='MACD Histogram Second Derivative')
ax[3].set_title('MACD Histogram Second Derivative')
ax[3].set_ylabel('MACD Hist Deriv2')
ax[3].legend(loc='upper left')
ax[3].grid()
plt.tight_layout()
plt.show()
