import sys
import types
import unittest

# Dummy dependencies so data.py imports cleanly
pandas = types.ModuleType("pandas")
pandas.DataFrame = lambda *a, **k: None
pandas.read_csv = lambda *a, **k: None
pandas.Series = lambda *a, **k: None
pandas.concat = lambda *a, **k: None
sys.modules.setdefault("pandas", pandas)

yfinance = types.ModuleType("yfinance")
yfinance.download = lambda *a, **k: types.SimpleNamespace(empty=False)
sys.modules.setdefault("yfinance", yfinance)

from data import fetch_price


class TestData(unittest.TestCase):
    """Example unit test for data fetching."""

    def test_fetch_price(self):
        df = fetch_price("AAPL")
        self.assertIsNotNone(df)
        self.assertFalse(df.empty, "Dataframe should not be empty")


if __name__ == "__main__":
    unittest.main()
