"""Social media scraping utilities."""

from typing import List
import re
import time
from pathlib import Path
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
    """Fetch recent tweets for given keywords using snscrape with retries.

    If scraping repeatedly fails, tweets are loaded from
    ``data/twitter_cache/<keyword>.txt`` where each line represents one tweet.
    """

    tweets: List[str] = []
    cache_dir = Path("data/twitter_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    for kw in keywords:
        attempt = 0
        success = False
        collected: List[str] = []
        while attempt < retries:
            try:
                scraper = sntwitter.TwitterSearchScraper(kw)
                for i, tweet in enumerate(scraper.get_items()):
                    collected.append(tweet.content)
                    if i + 1 >= limit:
                        break
                success = True
                break
            except Exception as exc:
                attempt += 1
                if attempt >= retries:
                    print(
                        f"Failed to scrape tweets for '{kw}' after {retries} attempts: {exc}"
                    )
                else:
                    time.sleep(delay * (2 ** attempt))

        file_name = f"{kw.replace(' ', '_')}.txt"
        cache_file = cache_dir / file_name

        if success:
            with cache_file.open("w", encoding="utf-8") as f:
                for line in collected:
                    f.write(clean_text(line) + "\n")
            tweets.extend(collected)
        else:
            if cache_file.exists():
                with cache_file.open("r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        line = line.strip()
                        if line:
                            tweets.append(line)
                        if i + 1 >= limit:
                            break
            else:
                print(f"No cached tweets found for '{kw}' in {cache_file}")
    return [clean_text(t) for t in tweets]


def get_reddit_posts(
    keywords: List[str],
    limit: int = 50,
    *,
    retries: int = 3,
    delay: float = 1.0,
) -> List[str]:
    """Fetch Reddit posts from Pushshift API with retries and caching."""
    posts: List[str] = []
    cache_dir = Path("data/reddit_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)

    for kw in keywords:
        url = f"https://api.pushshift.io/reddit/search/submission/?q={kw}&size={limit}"
        attempt = 0
        success = False
        collected: List[str] = []
        while attempt < retries:
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("data", []):
                        title = item.get("title") or ""
                        selftext = item.get("selftext") or ""
                        collected.append(f"{title} {selftext}")
                    success = True
                    break
            except Exception as exc:
                attempt += 1
                if attempt >= retries:
                    print(
                        f"Failed to scrape Reddit for '{kw}' after {retries} attempts: {exc}"
                    )
                else:
                    time.sleep(delay * (2 ** attempt))

        file_name = f"{kw.replace(' ', '_')}.txt"
        cache_file = cache_dir / file_name
        if success:
            with cache_file.open("w", encoding="utf-8") as f:
                for line in collected:
                    f.write(clean_text(line) + "\n")
            posts.extend(collected)
        else:
            if cache_file.exists():
                with cache_file.open("r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        line = line.strip()
                        if line:
                            posts.append(line)
                        if i + 1 >= limit:
                            break
            else:
                print(f"No cached reddit posts found for '{kw}' in {cache_file}")

    return [clean_text(p) for p in posts]
