"""Technical indicator computations."""

import pandas as pd
from technical_analysis import indicators as ta


def compute_rsi(df: pd.DataFrame, period: int = 14) -> float:
    """Compute RSI indicator."""
    if df.empty:
        return 0.0
    rsi_series = ta.rsi(df["Close"], length=period)
    return rsi_series.iloc[-1]


def compute_sma(df: pd.DataFrame, period: int) -> float:
    """Compute Simple Moving Average."""
    if df.empty:
        return 0.0
    sma = ta.sma(df["Close"], length=period)
    return sma.iloc[-1]


def compute_macd(df: pd.DataFrame) -> float:
    """Compute MACD and return last histogram value."""
    if df.empty:
        return 0.0
    macd_df = ta.macd(df["Close"])
    return macd_df["MACDh_12_26_9"].iloc[-1]
