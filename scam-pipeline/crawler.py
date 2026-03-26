"""
News crawler: fetch articles from RSS feeds and official sources.
"""

import re
from typing import Generator

import feedparser
import requests
from bs4 import BeautifulSoup

from config import NEWS_SOURCES


def fetch_rss(source_key: str) -> Generator[dict, None, None]:
    """Parse an RSS feed and yield article dicts."""
    source = NEWS_SOURCES.get(source_key)
    if not source:
        print(f"[crawler] Unknown source: {source_key}")
        return

    print(f"[crawler] Fetching RSS: {source['name']}  {source['rss']}")
    feed = feedparser.parse(source["rss"])
    needs_scrape = source.get("needs_scrape_title", False)

    for entry in feed.entries:
        title = entry.get("title", "")
        url = entry.get("link", "")
        summary = _clean(entry.get("summary", ""))

        if not title and needs_scrape and url:
            title = _scrape_title(url)

        if not title and not summary:
            continue
        if url and "Default.aspx" in url:
            continue

        yield {
            "title": title,
            "url": url,
            "published_at": entry.get("published", ""),
            "summary": summary,
            "source": source["name"],
        }


def fetch_article_text(url: str, timeout: int = 10) -> str:
    """Download a URL and extract the main text body."""
    try:
        resp = requests.get(url, timeout=timeout, headers={
            "User-Agent": "Mozilla/5.0 (FakeOff ScamPipeline)"
        })
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return _clean(text)
    except Exception as e:
        print(f"[crawler] Failed to fetch {url}: {e}")
        return ""


def fetch_all_sources(max_per_source: int = 20) -> list[dict]:
    """Fetch articles from all configured RSS sources."""
    all_articles = []
    for key in NEWS_SOURCES:
        count = 0
        for article in fetch_rss(key):
            all_articles.append(article)
            count += 1
            if count >= max_per_source:
                break
        print(f"[crawler] {NEWS_SOURCES[key]['name']}: {count} articles")
    return all_articles


def _scrape_title(url: str, timeout: int = 5) -> str:
    """Fetch a page and extract its <title> tag."""
    try:
        resp = requests.get(url, timeout=timeout, headers={
            "User-Agent": "Mozilla/5.0 (FakeOff ScamPipeline)"
        })
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        tag = soup.find("title")
        if tag:
            return tag.get_text(strip=True).split("|")[0].split("-")[0].strip()
    except Exception:
        pass
    return ""


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


if __name__ == "__main__":
    articles = fetch_all_sources(max_per_source=5)
    for a in articles:
        print(f"[{a['source']}] {a['title']}")
        print(f"  URL: {a['url']}")
        print(f"  Summary: {a['summary'][:80]}...")
        print()
