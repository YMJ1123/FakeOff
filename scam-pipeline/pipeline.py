"""
Main pipeline orchestrator.

Flow:
  1. Crawl news from RSS feeds
  2. Keyword filter + risk scoring
  3. LLM event analysis (medium/high risk only)
  4. Generate educational scam case summaries
  5. Store everything in SQLite
"""

import json
import sys

from analyzer import analyze_event
from case_generator import generate_cases
from crawler import fetch_all_sources, fetch_article_text
from db import (
    get_stats,
    init_db,
    insert_analysis,
    insert_case,
    insert_news,
)
from event_filter import filter_articles


def run_pipeline(max_per_source: int = 10, fetch_full_text: bool = True):
    """Run the full pipeline end-to-end."""
    init_db()

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
        print("No high-risk articles found. Pipeline done.")
        return

    # ── Step 3: Fetch full text & store ──────────────────────────
    print("\n" + "=" * 60)
    print("STEP 3: Fetching full text & storing in DB")
    print("=" * 60)
    stored = []
    for article in candidates:
        raw_text = article.get("summary", "")
        if fetch_full_text and article.get("url"):
            full = fetch_article_text(article["url"])
            if full:
                raw_text = full

        news_id = insert_news(
            title=article["title"],
            source=article.get("source", ""),
            url=article.get("url", ""),
            published_at=article.get("published_at", ""),
            raw_text=raw_text,
            summary=article.get("summary", ""),
            keyword_score=article["keyword_score"],
        )
        if news_id:
            article["news_id"] = news_id
            article["raw_text"] = raw_text
            stored.append(article)
            print(f"  Stored: [{news_id}] {article['title']}")
        else:
            print(f"  Skipped (duplicate): {article['title']}")

    # ── Step 4: LLM analysis ─────────────────────────────────────
    print("\n" + "=" * 60)
    print("STEP 4: LLM event analysis")
    print("=" * 60)
    analyzed = []
    for article in stored:
        text = article.get("raw_text") or article.get("summary", "")
        if not text:
            continue

        print(f"  Analyzing: {article['title'][:50]}...")
        try:
            analysis = analyze_event(text[:4000])
            insert_analysis(article["news_id"], analysis)
            article["analysis"] = analysis
            analyzed.append(article)
            potential = analysis.get("scam_potential", "?")
            print(f"    -> scam_potential: {potential}")
        except Exception as e:
            print(f"    -> Error: {e}")

    # ── Step 5: Generate cases ───────────────────────────────────
    print("\n" + "=" * 60)
    print("STEP 5: Generating scam case summaries")
    print("=" * 60)
    all_cases = []
    for article in analyzed:
        analysis = article.get("analysis", {})
        if analysis.get("scam_potential") == "low":
            print(f"  Skipping low-potential: {article['title'][:50]}")
            continue

        summary = article.get("summary") or article.get("raw_text", "")[:500]
        print(f"  Generating cases for: {article['title'][:50]}...")

        try:
            cases = generate_cases(summary, analysis)
            for case in cases:
                case_id = insert_case(article["news_id"], case)
                case["case_id"] = case_id
                all_cases.append(case)
            print(f"    -> Generated {len(cases)} cases")
        except Exception as e:
            print(f"    -> Error: {e}")

    # ── Summary ──────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    stats = get_stats()
    for table, count in stats.items():
        print(f"  {table}: {count} rows")


def run_demo():
    """Run a demo with hardcoded test data (no crawling needed)."""
    init_db()

    demo_articles = [
        {
            "title": "報稅截止日延長至6月底 國稅局提醒儘速完成申報",
            "summary": "財政部宣布今年報稅截止日延長，民眾可透過官方網站或APP線上申報退稅。逾期未申報者將依法處罰。",
            "url": "https://example.com/tax-2026",
            "published_at": "2026-03-26",
            "source": "中央社",
        },
        {
            "title": "銀行系統升級 部分用戶需重新驗證帳號",
            "summary": "某銀行公告系統升級期間，用戶可能收到簡訊通知需重新登入驗證身份確認，請至官方網站操作。",
            "url": "https://example.com/bank-upgrade",
            "published_at": "2026-03-26",
            "source": "ETtoday",
        },
    ]

    print("=== DEMO MODE ===\n")

    # Filter
    candidates = filter_articles(demo_articles)
    print(f"Filtered: {len(candidates)} candidates\n")

    for article in candidates:
        # Store
        news_id = insert_news(
            title=article["title"],
            source=article["source"],
            url=article["url"],
            published_at=article["published_at"],
            raw_text=article["summary"],
            summary=article["summary"],
            keyword_score=article["keyword_score"],
        )
        if not news_id:
            print(f"Skipped (duplicate): {article['title']}")
            continue

        print(f"[news_id={news_id}] {article['title']}")
        print(f"  Score: {article['keyword_score']}  Risk: {article['risk_level']}")
        print(f"  Keywords: {article['matched_keywords']}\n")

        # Analyze
        print("  -> Running LLM analysis...")
        analysis = analyze_event(article["summary"])
        insert_analysis(news_id, analysis)
        print(f"  -> Scam potential: {analysis.get('scam_potential')}")
        print(f"  -> Reason: {analysis.get('reason')}\n")

        # Generate cases
        if analysis.get("scam_potential") != "low":
            print("  -> Generating cases...")
            cases = generate_cases(article["summary"], analysis)
            for case in cases:
                case_id = insert_case(news_id, case)
                print(f"     Case [{case_id}]: {case.get('title')}")
            print()

    print("\n=== DB Stats ===")
    for table, count in get_stats().items():
        print(f"  {table}: {count}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "demo"

    if mode == "full":
        run_pipeline()
    elif mode == "demo":
        run_demo()
    else:
        print(f"Usage: python pipeline.py [demo|full]")
