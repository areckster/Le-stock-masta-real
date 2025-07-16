import unittest
from data import fetch_price


class TestData(unittest.TestCase):
    """Example unit test for data fetching."""

    def test_fetch_price(self):
        df = fetch_price("AAPL")
        self.assertIsNotNone(df)
        self.assertFalse(df.empty, "Dataframe should not be empty")


if __name__ == "__main__":
    unittest.main()
