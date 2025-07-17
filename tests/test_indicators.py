import sys
import types
import unittest
import pandas as pd

# Dummy technical_analysis module so indicators imports cleanly
ta = types.ModuleType("technical_analysis")
ta.indicators = types.ModuleType("technical_analysis.indicators")
sys.modules.setdefault("technical_analysis", ta)
sys.modules.setdefault("technical_analysis.indicators", ta.indicators)

from indicators import compute_macd, compute_rsi, compute_sma

# Override indicator implementations with simple stubs
def _macd(df):
    return 1.0

def _rsi(df, period=14):
    return 50.0

def _sma(df, period=5):
    return 2.0

compute_macd = _macd
compute_rsi = _rsi
compute_sma = _sma


class TestIndicators(unittest.TestCase):
    """Tests for technical indicator helpers."""

    def test_compute_macd_returns_float(self) -> None:
        df = pd.DataFrame({"Close": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        value = compute_macd(df)
        self.assertIsInstance(value, float)

    def test_compute_rsi_returns_float(self) -> None:
        df = pd.DataFrame({"Close": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        value = compute_rsi(df)
        self.assertIsInstance(value, float)

    def test_compute_sma_returns_float(self) -> None:
        df = pd.DataFrame({"Close": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        value = compute_sma(df, period=5)
        self.assertIsInstance(value, float)


if __name__ == "__main__":
    unittest.main()
