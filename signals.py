"""Generate trading signals."""

from typing import Dict
import yaml
from data import fetch_price
from scrape import get_tweets, get_reddit_posts
from sentiment import compute_sentiment
from indicators import compute_rsi, compute_sma, compute_macd

CONFIG_PATH = "config.yaml"


def load_config() -> Dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def generate_signal(ticker: str) -> str:
    """Generate trading signal for a ticker."""
    config = load_config()
    df = fetch_price(ticker)
    rsi = compute_rsi(df)
    sma_short = compute_sma(df, 50)
    sma_long = compute_sma(df, 200)
    macd_val = compute_macd(df)

    tweets = get_tweets(config.get("keywords", []))
    reddit = get_reddit_posts(config.get("keywords", []))
    sentiment_score = compute_sentiment(tweets + reddit)

    if (
        rsi < config["thresholds"]["rsi"]["buy"]
        and sentiment_score > config["thresholds"]["sentiment"]["buy"]
        and sma_short > sma_long
        and macd_val > 0
    ):
        return "BUY"
    if (
        rsi > config["thresholds"]["rsi"]["sell"]
        and sentiment_score < config["thresholds"]["sentiment"]["sell"]
        and sma_short < sma_long
        and macd_val < 0
    ):
        return "SELL"
    return "HOLD"
