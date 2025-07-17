import unittest
import pandas as pd

from indicators import compute_macd


class TestIndicators(unittest.TestCase):
    """Tests for technical indicator helpers."""

    def test_compute_macd_returns_float(self) -> None:
        df = pd.DataFrame({"Close": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        value = compute_macd(df)
        self.assertIsInstance(value, float)


if __name__ == "__main__":
    unittest.main()
