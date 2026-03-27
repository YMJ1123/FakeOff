"""
Main pipeline orchestrator.

Flow:
  1. Crawl news from RSS feeds
  2. Keyword filter + risk scoring
  3. LLM extracts scam tactics per article
  4. Build keyword-indexed knowledge base:
       keyword_category → [{title, scam_tactics, impersonation_targets}]
  5. Feed entire KB to conclusion agent for final judgment
"""

import json
import sys
from collections import defaultdict

from analyzer import extract_tactics
from conclusion_agent import run_conclusion
from crawler import fetch_all_sources, fetch_article_text
from event_filter import filter_articles


def build_keyword_index(articles: list[dict]) -> dict:
    """
    Group articles by their matched keyword categories.
    Returns: {category: [{title, scam_tactics, impersonation_targets}]}
    """
    index = defaultdict(list)

    for article in articles:
        matched = article.get("matched_keywords", {})
        title = article["title"]
        text = article.get("raw_text") or article.get("summary", "")

        print(f"  Extracting tactics: {title[:50]}...")
        try:
            tactics = extract_tactics(title, text)
        except Exception as e:
            print(f"    -> Error: {e}")
            tactics = {"scam_tactics": [], "impersonation_targets": [], "risk_level": "unknown"}

        risk = tactics.get("risk_level", "unknown")
        print(f"    -> risk: {risk}, tactics: {len(tactics.get('scam_tactics', []))}")

        entry = {
            "title": title,
            "url": article.get("url", ""),
            "source": article.get("source", ""),
            "published_at": article.get("published_at", ""),
            "scam_tactics": tactics.get("scam_tactics", []),
            "impersonation_targets": tactics.get("impersonation_targets", []),
            "keywords": tactics.get("keywords", []),
            "risk_level": risk,
        }

        for category in matched:
            index[category].append(entry)

    return dict(index)


def run_pipeline(max_per_source: int = 15, fetch_full_text: bool = False):
    """Run the full pipeline end-to-end."""

    # ── Step 1: Crawl ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("STEP 1: Crawling news sources")
    print("=" * 60)
    articles = fetch_all_sources(max_per_source=max_per_source)
    print(f"Total articles fetched: {len(articles)}")

    # ── Step 2: Keyword filter ───────────────────────────────────
    print("\n" + "=" * 60)
    print("STEP 2: Keyword filtering & risk scoring")
    print("=" * 60)
    candidates = filter_articles(articles)
    print(f"Candidates after filtering: {len(candidates)} / {len(articles)}")
    for c in candidates:
        print(f"  [{c['risk_level'].upper()} score={c['keyword_score']}] {c['title']}")

    if not candidates:
        print("\nNo high-risk articles found. Pipeline done.")
        return

    # ── Step 2.5: Optionally fetch full text ─────────────────────
    if fetch_full_text:
        print("\n  Fetching full article text...")
        for article in candidates:
            if article.get("url"):
                full = fetch_article_text(article["url"])
                if full:
                    article["raw_text"] = full

    # ── Step 3: Extract tactics & build keyword index ────────────
    print("\n" + "=" * 60)
    print("STEP 3: Extracting scam tactics & building keyword index")
    print("=" * 60)
    keyword_index = build_keyword_index(candidates)

    print(f"\n  Keyword index built with {len(keyword_index)} categories:")
    for cat, entries in keyword_index.items():
        print(f"    {cat}: {len(entries)} articles")

    # ── Step 4: Conclusion agent ─────────────────────────────────
    print("\n" + "=" * 60)
    print("STEP 4: Conclusion agent — final judgment")
    print("=" * 60)
    conclusion = run_conclusion(keyword_index)

    # ── Output ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("KEYWORD INDEX (input to conclusion model)")
    print("=" * 60)
    print(json.dumps(keyword_index, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("CONCLUSION (final judgment)")
    print("=" * 60)
    print(json.dumps(conclusion, ensure_ascii=False, indent=2))

    # Save to files
    with open("keyword_index.json", "w", encoding="utf-8") as f:
        json.dump(keyword_index, f, ensure_ascii=False, indent=2)
    with open("conclusion.json", "w", encoding="utf-8") as f:
        json.dump(conclusion, f, ensure_ascii=False, indent=2)
    print("\nSaved: keyword_index.json, conclusion.json")


def run_demo():
    """Run a demo with hardcoded test data."""
    demo_articles = [
        {
            "title": "報稅截止日延長至6月底 國稅局提醒儘速完成申報",
            "summary": "財政部宣布今年報稅截止日延長，民眾可透過官方網站或APP線上申報退稅。逾期未申報者將依法處罰。",
            "source": "自由時報",
            "url": "https://news.ltn.com.tw/news/life/example1",
            "published_at": "2026-03-25",
        },
        {
            "title": "銀行系統升級 部分用戶需重新驗證帳號",
            "summary": "某銀行公告系統升級期間，用戶可能收到簡訊通知需重新登入驗證身份確認，請至官方網站操作。",
            "source": "ETtoday",
            "url": "https://www.ettoday.net/news/example2",
            "published_at": "2026-03-24",
        },
        {
            "title": "青創補助再加碼 旗山說明會引爆創業熱 申請延至4/15",
            "summary": "高雄市政府青年局青創補助計畫再加碼，旗山說明會吸引大量青年參與，申請截止日延長至4月15日。",
            "source": "Yahoo新聞",
            "url": "https://tw.news.yahoo.com/example3",
            "published_at": "2026-03-23",
        },
    ]

    print("=== DEMO MODE ===\n")

    # Filter
    candidates = filter_articles(demo_articles)
    print(f"Filtered: {len(candidates)} candidates\n")
    for c in candidates:
        print(f"  [{c['risk_level'].upper()} score={c['keyword_score']}] {c['title']}")
        print(f"    keywords: {c['matched_keywords']}")

    if not candidates:
        print("No candidates. Done.")
        return

    # Build keyword index
    print(f"\n--- Extracting scam tactics ---")
    keyword_index = build_keyword_index(candidates)

    print(f"\n--- Keyword Index ---")
    print(json.dumps(keyword_index, ensure_ascii=False, indent=2))

    # Conclusion
    print(f"\n--- Running conclusion agent ---")
    conclusion = run_conclusion(keyword_index)

    print(f"\n--- Final Conclusion ---")
    print(json.dumps(conclusion, ensure_ascii=False, indent=2))

    with open("keyword_index.json", "w", encoding="utf-8") as f:
        json.dump(keyword_index, f, ensure_ascii=False, indent=2)
    with open("conclusion.json", "w", encoding="utf-8") as f:
        json.dump(conclusion, f, ensure_ascii=False, indent=2)
    print("\nSaved: keyword_index.json, conclusion.json")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "demo"

    if mode == "full":
        run_pipeline()
    elif mode == "demo":
        run_demo()
    else:
        print("Usage: python pipeline.py [demo|full]")
