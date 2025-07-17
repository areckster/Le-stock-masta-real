import sys
import types
import unittest
from unittest.mock import patch

_sns = types.ModuleType("snscrape")
_sns_modules = types.ModuleType("snscrape.modules")
_sns_twitter = types.ModuleType("snscrape.modules.twitter")
_sns_twitter.TwitterSearchScraper = object
_sns_modules.twitter = _sns_twitter
_sns.modules = _sns_modules
sys.modules["snscrape"] = _sns
sys.modules["snscrape.modules"] = _sns_modules
sys.modules["snscrape.modules.twitter"] = _sns_twitter

dummy_aps = types.ModuleType("apscheduler")
dummy_sched = types.ModuleType("apscheduler.schedulers")
dummy_back = types.ModuleType("apscheduler.schedulers.background")
dummy_back.BackgroundScheduler = object
dummy_sched.background = dummy_back
dummy_aps.schedulers = dummy_sched
sys.modules["apscheduler"] = dummy_aps
sys.modules["apscheduler.schedulers"] = dummy_sched
sys.modules["apscheduler.schedulers.background"] = dummy_back

# Stub yaml module required by signals.load_config
dummy_yaml = types.ModuleType("yaml")
dummy_yaml.safe_load = lambda *a, **k: {}
sys.modules.setdefault("yaml", dummy_yaml)

# Dummy requests module for scrape dependency
sys.modules.setdefault("requests", types.ModuleType("requests"))

# Dummy pandas and yfinance for data module
pandas = types.ModuleType("pandas")
pandas.DataFrame = object
sys.modules.setdefault("pandas", pandas)

yfinance = types.ModuleType("yfinance")
yfinance.download = lambda *a, **k: types.SimpleNamespace(empty=False)
sys.modules.setdefault("yfinance", yfinance)

dummy_transformers = types.ModuleType("transformers")
dummy_transformers.AutoModelForSequenceClassification = object
dummy_transformers.AutoTokenizer = object
dummy_transformers.pipeline = lambda *a, **k: None
sys.modules["transformers"] = dummy_transformers

for name in [
    "torch",
    "technical_analysis",
    "technical_analysis.indicators",
]:
    sys.modules.setdefault(name, types.ModuleType(name))

dummy_webhook = types.ModuleType("discord_webhook")
dummy_webhook.DiscordWebhook = object
sys.modules["discord_webhook"] = dummy_webhook

import run_scheduler


class FakeScheduler:
    def __init__(self):
        self.minutes = None

    def add_job(self, func, trigger, *, minutes=None):
        self.minutes = minutes

    def start(self):
        pass

    def shutdown(self):
        pass


class TestScheduler(unittest.TestCase):
    def test_uses_config_interval(self):
        fake = FakeScheduler()
        config = {"schedule": {"every": "5 minutes"}}
        with patch("run_scheduler.load_config", return_value=config), \
             patch("run_scheduler.BackgroundScheduler", return_value=fake), \
             patch("run_scheduler.time.sleep", side_effect=KeyboardInterrupt):
            run_scheduler.start()
        self.assertEqual(fake.minutes, 5)


if __name__ == "__main__":
    unittest.main()
