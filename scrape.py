"""Social media scraping utilities."""

from typing import List
import re
import time
import requests
import snscrape.modules.twitter as sntwitter


def clean_text(text: str) -> str:
    """Simple text cleaner for sentiment analysis."""
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text.strip().lower()


def get_tweets(
    keywords: List[str],
    limit: int = 50,
    *,
    retries: int = 3,
    delay: float = 1.0,
) -> List[str]:
    """Fetch recent tweets for given keywords using snscrape with retries."""

    tweets: List[str] = []
    for kw in keywords:
        attempt = 0
        while attempt < retries:
            try:
                scraper = sntwitter.TwitterSearchScraper(kw)
                for i, tweet in enumerate(scraper.get_items()):
                    tweets.append(tweet.content)
                    if i + 1 >= limit:
                        break
                break
            except Exception as exc:
                attempt += 1
                if attempt >= retries:
                    print(
                        f"Failed to scrape tweets for '{kw}' after {retries} attempts: {exc}"
                    )
                else:
                    time.sleep(delay * (2 ** attempt))
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
