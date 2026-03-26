"""
Keyword-based event filter and risk scoring.
First-pass filter before sending to LLM — cheap and fast.
"""

from config import SCAM_KEYWORDS, SCORE_THRESHOLD_LOW, SCORE_THRESHOLD_MEDIUM


def score_article(text: str) -> tuple[int, dict[str, list[str]]]:
    """
    Score an article based on keyword matches.
    Returns (total_score, {category: [matched_keywords]}).
    """
    total = 0
    matched = {}

    for category, cfg in SCAM_KEYWORDS.items():
        hits = [w for w in cfg["words"] if w in text]
        if hits:
            total += cfg["weight"]
            matched[category] = hits

    return total, matched


def classify_risk(score: int) -> str:
    if score <= SCORE_THRESHOLD_LOW:
        return "low"
    elif score <= SCORE_THRESHOLD_MEDIUM:
        return "medium"
    else:
        return "high"


def filter_articles(articles: list[dict]) -> list[dict]:
    """
    Score and classify a list of articles.
    Only returns medium/high risk articles.
    """
    results = []
    for article in articles:
        text = f"{article.get('title', '')} {article.get('summary', '')} {article.get('raw_text', '')}"
        score, matched = score_article(text)
        risk = classify_risk(score)

        article["keyword_score"] = score
        article["matched_keywords"] = matched
        article["risk_level"] = risk

        if risk in ("medium", "high"):
            results.append(article)

    results.sort(key=lambda x: x["keyword_score"], reverse=True)
    return results


if __name__ == "__main__":
    test_articles = [
        {
            "title": "報稅截止日延長至6月底 國稅局提醒儘速完成申報",
            "summary": "財政部宣布今年報稅截止日延長，民眾可透過官方網站或APP線上申報退稅。",
        },
        {
            "title": "新北市週末天氣晴朗 適合出遊",
            "summary": "氣象局預報本週末天氣穩定，各地晴到多雲。",
        },
        {
            "title": "銀行系統升級 部分用戶需重新驗證帳號",
            "summary": "某銀行公告系統升級期間，用戶可能收到簡訊通知需重新登入驗證身份。",
        },
    ]

    filtered = filter_articles(test_articles)
    for a in filtered:
        print(f"[{a['risk_level'].upper()} score={a['keyword_score']}] {a['title']}")
        print(f"  Matched: {a['matched_keywords']}")
        print()
