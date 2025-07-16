"""Backtesting utilities using backtrader."""

import backtrader as bt
import pandas as pd
import yaml
from data import fetch_price
from scrape import get_tweets, get_reddit_posts
from sentiment import compute_sentiment

CONFIG_PATH = "config.yaml"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


class SignalStrategy(bt.Strategy):
    params = dict(config=None, sentiment=0.0)

    def __init__(self):
        self.order = None
        self.rsi = bt.indicators.RSI(self.data.close, period=14)

    def next(self):
        if self.order:
            return
        cfg = self.p.config
        if (
            not self.position
            and self.rsi[0] < cfg["thresholds"]["rsi"]["buy"]
            and self.p.sentiment > cfg["thresholds"]["sentiment"]["buy"]
        ):
            self.order = self.buy()
        elif (
            self.position
            and self.rsi[0] > cfg["thresholds"]["rsi"]["sell"]
            and self.p.sentiment < cfg["thresholds"]["sentiment"]["sell"]
        ):
            self.order = self.sell()


def backtest_strategy(ticker: str):
    """Run backtest and return performance metrics."""
    config = load_config()
    df = fetch_price(ticker, period="1y", interval="1d")
    sentiment_score = compute_sentiment(
        get_tweets(config.get("keywords", []))
        + get_reddit_posts(config.get("keywords", []))
    )

    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.addstrategy(
        SignalStrategy, config=config, sentiment=sentiment_score
    )
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    result = cerebro.run()[0]
    sharpe = result.analyzers.sharpe.get_analysis().get("sharperatio", 0.0)
    dd = result.analyzers.drawdown.get_analysis().get("max", 0.0)
    final_value = cerebro.broker.getvalue()
    print(f"Final portfolio value: {final_value}")
    return {
        "sharpe": sharpe,
        "drawdown": dd,
    }
