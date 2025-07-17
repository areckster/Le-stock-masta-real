"""Data fetching utilities."""

from __future__ import annotations
import time

import pandas as pd
import yfinance as yf


def fetch_price(
    ticker: str,
    *,
    period: str = "6mo",
    interval: str = "1d",
    retries: int = 3,
    delay: float = 1.0,
) -> pd.DataFrame:
    """Fetch historical price data for a ticker with retry logic.

    Parameters
    ----------
    ticker: str
        Stock symbol to fetch.
    retries: int
        Number of attempts before failing.
    delay: float
        Base delay between retries in seconds.

    Returns
    -------
    pd.DataFrame
        Price dataframe provided by yfinance.
    """
    attempt = 0
    while attempt < retries:
        try:
            df = yf.download(
                ticker,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=False,
            )
            if not df.empty:
                return df
        except Exception as exc:
            print(f"Error fetching {ticker}: {exc}")
        attempt += 1
        time.sleep(delay * (2 ** attempt))
    return pd.DataFrame()
