import unittest
import shutil
from pathlib import Path
from unittest.mock import patch

import types
import sys

# Dummy requests module so scrape imports cleanly
sys.modules.setdefault('requests', types.ModuleType('requests'))

import scrape


class TestScrapeFallback(unittest.TestCase):
    def tearDown(self) -> None:
        for pattern in ('*_tweets.csv',):
            for p in Path('.').glob(pattern):
                p.unlink()
        shutil.rmtree('data', ignore_errors=True)

    def test_twint_used_when_playwright_fails(self):
        with patch('scrape.fetch_with_playwright', return_value=[]), \
             patch('scrape.fetch_with_twint', return_value=[{
                 'date': '2020',
                 'tweet_id': '1',
                 'content': 'twint tweet',
                 'username': 'user'
             }]), \
             patch('scrape.fetch_from_nitter', return_value=[]):
            tweets = scrape.get_tweets(['stock market'], retries=1, limit=1)
        self.assertEqual(tweets, ['twint tweet'])
        self.assertTrue(Path('stock_market_tweets.csv').exists())

    def test_nitter_used_when_others_fail(self):
        with patch('scrape.fetch_with_playwright', return_value=[]), \
             patch('scrape.fetch_with_twint', return_value=[]), \
             patch('scrape.fetch_from_nitter', return_value=[{
                 'date': '2020',
                 'tweet_id': '2',
                 'content': 'nitter tweet',
                 'username': 'user'
             }]):
            tweets = scrape.get_tweets(['tech stocks'], retries=1, limit=1)
        self.assertEqual(tweets, ['nitter tweet'])
        self.assertTrue(Path('tech_stocks_tweets.csv').exists())

    def test_nitter_invalid_json_returns_empty(self):
        class DummyResp:
            status_code = 200
            def json(self):
                raise ValueError('bad json')
        with patch.object(scrape.requests, 'get', return_value=DummyResp(), create=True):
            tweets = scrape.fetch_from_nitter('query', 5)
        self.assertEqual(tweets, [])

if __name__ == '__main__':
    unittest.main()
