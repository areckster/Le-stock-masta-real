"""Social media scraping utilities."""

from typing import List
import re
import time
from pathlib import Path
import requests
import snscrape.modules.twitter as sntwitter


def fetch_with_playwright(query: str, limit: int, *, headless: bool = True) -> List[str]:
    """Fetch tweets with Playwright as a last resort.

    Parameters
    ----------
    query:
        Search query.
    limit:
        Maximum number of tweets to return.
    headless:
        Whether to run the browser in headless mode.

    Returns
    -------
    List[str]
        Raw tweet texts or an empty list on failure.
    """

    try:  # pragma: no cover - optional dependency
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover
        print(f"playwright not available: {exc}")
        return []

    tweets: List[str] = []
    url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"

    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=headless)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            last_height = 0
            while len(tweets) < limit:
                # allow extra time for the page to load when network
                # conditions are poor
                page.wait_for_selector("article", timeout=30000)
                articles = page.query_selector_all("article")
                for article in articles[len(tweets) :]:
                    text = article.inner_text()
                    if text:
                        tweets.append(text)
                        if len(tweets) >= limit:
                            break
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                height = page.evaluate("document.body.scrollHeight")
                if height == last_height:
                    break
                last_height = height
            browser.close()
    except Exception as exc:  # pragma: no cover - network/browser errors
        print(f"fetch_with_playwright failed for '{query}': {exc}")
        return []

    return tweets[:limit]


def clean_text(text: str) -> str:
    """Simple text cleaner for sentiment analysis."""
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text.strip().lower()


def fetch_from_nitter(query: str, limit: int, instance: str = "https://nitter.net") -> List[str]:
    """Fetch tweets from a Nitter instance as a JSON fallback."""
    url = f"{instance}/search?f=tweets&q={query}&format=json"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return []
        try:
            data = resp.json()
        except Exception as exc:
            print(f"fetch_from_nitter failed for '{query}' - invalid JSON: {exc}")
            return []

        results: List[str] = []
        items = data.get("results") or data.get("tweets") or data
        for item in items:
            if isinstance(item, dict):
                text = item.get("text") or item.get("tweet", {}).get("text")
                if text:
                    results.append(text)
                    if len(results) >= limit:
                        break
        return results
    except Exception as exc:  # pragma: no cover - network errors
        print(f"fetch_from_nitter failed for '{query}': {exc}")
    return []


def get_tweets(
    keywords: List[str],
    limit: int = 50,
    *,
    retries: int = 3,
    delay: float = 1.0,
) -> List[str]:
    """Fetch recent tweets for given keywords.

    The primary method uses ``snscrape`` with retry logic. If all attempts fail,
    the function tries a Nitter instance via :func:`fetch_from_nitter`. When both
    methods fail, tweets are loaded from ``data/twitter_cache/<keyword>.txt``.
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

        if not success:
            try:
                collected = fetch_from_nitter(kw, limit)
            except Exception as exc:  # pragma: no cover
                print(f"fetch_from_nitter failed for '{kw}': {exc}")
                collected = []
            if collected:
                success = True

        if not success:
            try:
                collected = fetch_with_playwright(kw, limit)
            except Exception as exc:  # pragma: no cover
                print(f"fetch_with_playwright failed for '{kw}': {exc}")
                collected = []
            if collected:
                success = True

        if success:
            try:
                with cache_file.open("w", encoding="utf-8") as f:
                    for line in collected:
                        f.write(clean_text(line) + "\n")
            except Exception as exc:  # pragma: no cover - disk errors
                print(f"Failed to write cache for '{kw}' in {cache_file}: {exc}")
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
