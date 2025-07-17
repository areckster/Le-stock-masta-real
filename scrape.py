"""Utilities for scraping Twitter and Reddit sentiment."""

from __future__ import annotations

import csv
import logging
import time
from pathlib import Path
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Twitter helpers
# ---------------------------------------------------------------------------

def fetch_with_playwright(query: str, limit: int, *, headless: bool = True) -> List[Dict[str, str]]:
    """Scrape tweets using Playwright."""
    try:  # pragma: no cover - optional dependency
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover - import errors
        logger.error("playwright not available: %s", exc)
        return []

    tweets: List[Dict[str, str]] = []
    url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
    try:  # pragma: no cover - network/browser errors
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=headless)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            last_height = 0
            while len(tweets) < limit:
                page.wait_for_selector("article", timeout=30000)
                articles = page.query_selector_all("article")
                for article in articles[len(tweets):]:
                    text = article.inner_text()
                    link = article.query_selector("a[href*='/status/']")
                    time_el = article.query_selector("time")
                    if not (text and link and time_el):
                        continue
                    href = link.get_attribute("href") or ""
                    parts = href.strip("/").split("/")
                    if len(parts) >= 3:
                        username = parts[0]
                        tweet_id = parts[2]
                    else:
                        continue
                    date = time_el.get_attribute("datetime") or ""
                    tweets.append(
                        {
                            "date": date,
                            "tweet_id": tweet_id,
                            "content": text,
                            "username": username,
                        }
                    )
                    if len(tweets) >= limit:
                        break
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                height = page.evaluate("document.body.scrollHeight")
                if height == last_height:
                    break
                last_height = height
            browser.close()
    except Exception as exc:
        logger.error("fetch_with_playwright failed for '%s': %s", query, exc)
        return []
    return tweets[:limit]


def fetch_with_twint(query: str, limit: int) -> List[Dict[str, str]]:
    """Scrape tweets with Twint."""
    try:  # pragma: no cover - optional dependency
        import pandas as pd
        import twint
    except Exception as exc:  # pragma: no cover
        logger.error("twint not available: %s", exc)
        return []

    c = twint.Config()
    c.Search = query
    c.Limit = limit
    c.Hide_output = True
    c.Pandas = True

    try:  # pragma: no cover - network errors
        twint.run.Search(c)
        df = twint.storage.panda.Tweets_df
    except Exception as exc:
        logger.error("twint search failed for '%s': %s", query, exc)
        return []

    results: List[Dict[str, str]] = []
    for _, row in df.iterrows():
        results.append(
            {
                "date": str(row.get("date")),
                "tweet_id": str(row.get("id")),
                "content": row.get("tweet", ""),
                "username": row.get("username", ""),
            }
        )
        if len(results) >= limit:
            break

    twint.storage.panda.Tweets_df = pd.DataFrame()
    return results


def fetch_from_nitter(query: str, limit: int, instance: str = "https://nitter.net") -> List[Dict[str, str]]:
    """Fetch tweets from a Nitter instance."""
    try:
        resp = requests.get(
            f"{instance}/search",
            params={"f": "tweets", "q": query, "format": "json"},
            timeout=10,
        )
        if resp.status_code != 200:
            return []
        try:
            data = resp.json()
        except Exception as exc:  # pragma: no cover - invalid JSON
            logger.error("fetch_from_nitter failed for '%s' - invalid JSON: %s", query, exc)
            return []

        results: List[Dict[str, str]] = []
        items = data.get("results") or data.get("tweets") or data
        for item in items:
            if not isinstance(item, dict):
                continue
            text = item.get("text") or item.get("tweet", {}).get("text")
            tweet_id = str(item.get("id") or item.get("tweetId") or "")
            username = item.get("username") or item.get("user", {}).get("username", "")
            date = item.get("date") or item.get("created_at") or ""
            if text:
                results.append(
                    {
                        "date": str(date),
                        "tweet_id": tweet_id,
                        "content": text,
                        "username": username,
                    }
                )
                if len(results) >= limit:
                    break
        return results
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("fetch_from_nitter failed for '%s': %s", query, exc)
    return []


# ---------------------------------------------------------------------------
# Reddit helpers
# ---------------------------------------------------------------------------

def fetch_pushshift(query: str, limit: int) -> List[Dict[str, str]]:
    """Fetch Reddit posts using the Pushshift API."""
    url = f"https://api.pushshift.io/reddit/search/submission/?q={query}&size={limit}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return []
        data = resp.json()
        results: List[Dict[str, str]] = []
        for item in data.get("data", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "score": item.get("score", 0),
                    "num_comments": item.get("num_comments", 0),
                    "url": item.get("full_link") or item.get("url", ""),
                }
            )
            if len(results) >= limit:
                break
        return results
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("fetch_pushshift failed for '%s': %s", query, exc)
        return []


def fetch_reddit_api(
    query: str,
    limit: int,
    *,
    client_id: str = "",
    client_secret: str = "",
    user_agent: str = "stock-scraper",
) -> List[Dict[str, str]]:
    """Fetch Reddit posts using the official API."""
    try:
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        data = {"grant_type": "client_credentials"}
        headers = {"User-Agent": user_agent}
        token_resp = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data=data,
            headers=headers,
            timeout=10,
        )
        token = token_resp.json().get("access_token")
        if not token:
            return []
        headers["Authorization"] = f"bearer {token}"
        search_resp = requests.get(
            "https://oauth.reddit.com/search",
            params={"q": query, "limit": limit, "sort": "new"},
            headers=headers,
            timeout=10,
        )
        if search_resp.status_code != 200:
            return []
        data = search_resp.json()
        results: List[Dict[str, str]] = []
        for child in data.get("data", {}).get("children", []):
            item = child.get("data", {})
            results.append(
                {
                    "title": item.get("title", ""),
                    "score": item.get("score", 0),
                    "num_comments": item.get("num_comments", 0),
                    "url": item.get("url", ""),
                }
            )
            if len(results) >= limit:
                break
        return results
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("fetch_reddit_api failed for '%s': %s", query, exc)
        return []


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Simple text cleaner."""
    import re

    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text.strip().lower()


def append_unique_csv(file_path: Path, rows: List[Dict[str, str]], *, key_field: str, headers: List[str]) -> None:
    """Append rows to ``file_path`` ensuring ``key_field`` uniqueness."""
    existing = set()
    if file_path.exists():
        with file_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row.get(key_field))
    with file_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if f.tell() == 0:
            writer.writeheader()
        for row in rows:
            if row.get(key_field) not in existing:
                writer.writerow(row)
                existing.add(row.get(key_field))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_tweets(
    keywords: List[str],
    limit: int = 50,
    *,
    retries: int = 3,
    delay: float = 1.0,
) -> List[str]:
    """Fetch recent tweets and store them in CSV files."""
    texts: List[str] = []
    for kw in keywords:
        csv_file = Path(f"{kw.replace(' ', '_')}_tweets.csv")
        attempt = 0
        success = False
        print(f"Fetching tweets for '{kw}'")
        results: List[Dict[str, str]] = []
        while attempt < retries:
            print(f"Playwright attempt {attempt + 1} for '{kw}'")
            results = fetch_with_playwright(kw, limit)
            if results:
                print(f"Playwright succeeded for '{kw}'")
                success = True
                break
            attempt += 1
            time.sleep(delay * (2 ** attempt))
        if not success:
            print(f"Falling back to Twint for '{kw}'")
            attempt = 0
            while attempt < retries:
                print(f"Twint attempt {attempt + 1} for '{kw}'")
                results = fetch_with_twint(kw, limit)
                if results:
                    print(f"Twint succeeded for '{kw}'")
                    success = True
                    break
                attempt += 1
                time.sleep(delay * (2 ** attempt))
        if not success:
            print(f"Falling back to Nitter for '{kw}'")
            results = fetch_from_nitter(kw, limit)
            success = bool(results)
            if success:
                print(f"Nitter succeeded for '{kw}'")

        if success:
            append_unique_csv(
                csv_file,
                results,
                key_field="tweet_id",
                headers=["date", "tweet_id", "content", "username"],
            )
            texts.extend(clean_text(r["content"]) for r in results)
        else:
            logger.error("all twitter methods failed for '%s'", kw)
            print(f"Failed to fetch tweets for '{kw}'")
    return texts


def get_reddit_posts(
    keywords: List[str],
    limit: int = 50,
    *,
    retries: int = 3,
    delay: float = 1.0,
    client_id: str = "",
    client_secret: str = "",
) -> List[str]:
    """Fetch Reddit posts and store them in CSV files."""
    texts: List[str] = []
    for kw in keywords:
        csv_file = Path(f"{kw.replace(' ', '_')}_reddit.csv")
        attempt = 0
        success = False
        print(f"Fetching Reddit posts for '{kw}'")
        results: List[Dict[str, str]] = []
        while attempt < retries:
            print(f"Pushshift attempt {attempt + 1} for '{kw}'")
            results = fetch_pushshift(kw, limit)
            if results:
                print(f"Pushshift succeeded for '{kw}'")
                success = True
                break
            attempt += 1
            time.sleep(delay * (2 ** attempt))
        if not success:
            print(f"Falling back to Reddit API for '{kw}'")
            results = fetch_reddit_api(
                kw,
                limit,
                client_id=client_id,
                client_secret=client_secret,
            )
            success = bool(results)
            if success:
                print(f"Reddit API succeeded for '{kw}'")

        if success:
            append_unique_csv(
                csv_file,
                results,
                key_field="url",
                headers=["title", "score", "num_comments", "url"],
            )
            texts.extend(clean_text(r["title"]) for r in results)
        else:
            logger.error("all reddit methods failed for '%s'", kw)
            print(f"Failed to fetch Reddit posts for '{kw}'")
    return texts

