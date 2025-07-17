import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

import types
import sys

# Provide dummy requests and snscrape modules so scrape imports cleanly
sys.modules.setdefault('requests', types.ModuleType('requests'))

_sns = types.ModuleType('snscrape')
_sns_modules = types.ModuleType('snscrape.modules')
_sns_twitter = types.ModuleType('snscrape.modules.twitter')
_sns_twitter.TwitterSearchScraper = object
_sns_modules.twitter = _sns_twitter
_sns.modules = _sns_modules
sys.modules['snscrape'] = _sns
sys.modules['snscrape.modules'] = _sns_modules
sys.modules['snscrape.modules.twitter'] = _sns_twitter

import scrape


class TestScrapeFallback(unittest.TestCase):
    def test_loads_cache_on_failure(self):
        cache_dir = Path('data/twitter_cache')
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / 'test.txt').write_text('cached tweet\n')

        with patch('scrape.sntwitter.TwitterSearchScraper') as mock_scraper:
            mock_scraper.return_value.get_items.side_effect = Exception('fail')
            tweets = scrape.get_tweets(['test'], retries=1)
        self.assertEqual(tweets, ['cached tweet'])

        shutil.rmtree('data')


if __name__ == '__main__':
    unittest.main()
