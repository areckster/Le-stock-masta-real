"""Social media scraping utilities."""

from typing import List
import re
import requests
import snscrape.modules.twitter as sntwitter


def clean_text(text: str) -> str:
    """Simple text cleaner for sentiment analysis."""
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text.strip().lower()


def get_tweets(keywords: List[str], limit: int = 50) -> List[str]:
    """Fetch recent tweets for given keywords using snscrape."""
    tweets: List[str] = []
    for kw in keywords:
        try:
            scraper = sntwitter.TwitterSearchScraper(kw)
            for i, tweet in enumerate(scraper.get_items()):
                tweets.append(tweet.content)
                if i + 1 >= limit:
                    break
        except Exception as exc:
            print(f"Error scraping tweets for '{kw}': {exc}")
    return [clean_text(t) for t in tweets]


def get_reddit_posts(keywords: List[str], limit: int = 50) -> List[str]:
    """Fetch Reddit posts from Pushshift API."""
    posts: List[str] = []
    for kw in keywords:
        url = f"https://api.pushshift.io/reddit/search/submission/?q={kw}&size={limit}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("data", []):
                    title = item.get("title") or ""
                    selftext = item.get("selftext") or ""
                    posts.append(f"{title} {selftext}")
        except Exception as exc:
            print(f"Error scraping Reddit for '{kw}': {exc}")
    return [clean_text(p) for p in posts]
