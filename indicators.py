"""Technical indicator computations."""

import pandas as pd
from technical_analysis import indicators as ta


def compute_rsi(df: pd.DataFrame, period: int = 14) -> float:
    """Compute the Relative Strength Index.

    Parameters
    ----------
    df : pd.DataFrame
        Price dataframe containing a ``Close`` column.
    period : int, optional
        Number of periods used to compute the indicator. Defaults to ``14``.

    Returns
    -------
    float
        The most recent RSI value. ``0.0`` if ``df`` is empty.
    """
    if df.empty:
        return 0.0
    rsi_series = ta.rsi(df["Close"], period=period)
    return float(rsi_series.iloc[-1].item())


def compute_sma(df: pd.DataFrame, period: int) -> float:
    """Compute the Simple Moving Average.

    Parameters
    ----------
    df : pd.DataFrame
        Price dataframe containing a ``Close`` column.
    period : int
        Number of periods used for the average.

    Returns
    -------
    float
        The most recent SMA value. ``0.0`` if ``df`` is empty.
    """
    if df.empty:
        return 0.0
    sma = ta.sma(df["Close"], period=period)
    return float(sma.iloc[-1].item())


def compute_macd(df: pd.DataFrame) -> float:
    """Compute MACD histogram and return the last value.

    Parameters
    ----------
    df : pd.DataFrame
        Price dataframe containing a ``Close`` column.

    Returns
    -------
    float
        The most recent MACD histogram value. ``0.0`` if ``df`` is empty.
    """
    if df.empty:
        return 0.0

    # ``ta.macd`` returns a Series containing the MACD histogram values.
    macd_series = ta.macd(df["Close"])
    return float(macd_series.iloc[-1].item())
