"""
Keyword Check module — the "keyword check" box in the architecture.

Takes user input text, matches it against the keyword index,
and returns relevant news events + scam tactics as context
for the Conclusion Agent.
"""

import json
from pathlib import Path

from config import SCAM_KEYWORDS

KEYWORD_INDEX_PATH = Path(__file__).parent / "keyword_index.json"


def load_keyword_index(path: str = None) -> dict:
    p = Path(path) if path else KEYWORD_INDEX_PATH
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def match_user_input(user_text: str, keyword_index: dict = None) -> dict:
    """
    Match user input against the keyword index.

    Returns:
        {
            "matched_categories": {category: [matched_words]},
            "matched_context": {category: [{title, scam_tactics, ...}]},
            "match_score": int,
            "has_match": bool,
        }
    """
    if keyword_index is None:
        keyword_index = load_keyword_index()

    matched_categories = {}
    matched_context = {}

    for category, cfg in SCAM_KEYWORDS.items():
        hits = [w for w in cfg["words"] if w in user_text]
        if hits:
            matched_categories[category] = hits
            if category in keyword_index:
                matched_context[category] = keyword_index[category]

    score = sum(
        SCAM_KEYWORDS[cat]["weight"] for cat in matched_categories
    )

    return {
        "matched_categories": matched_categories,
        "matched_context": matched_context,
        "match_score": score,
        "has_match": len(matched_context) > 0,
    }


def format_context_for_conclusion(user_text: str, match_result: dict) -> dict:
    """
    Package user input + matched keyword context into a structured
    payload ready for the Conclusion Agent.
    """
    return {
        "user_input": user_text,
        "match_score": match_result["match_score"],
        "matched_categories": match_result["matched_categories"],
        "relevant_news_and_tactics": match_result["matched_context"],
    }


if __name__ == "__main__":
    test_inputs = [
        "我收到國稅局的簡訊說我退稅失敗，要我點連結重新驗證身份",
        "銀行通知我帳號異常需要重新登入驗證",
        "有人說可以幫我加速青創補助審核，要先繳保證金",
        "今天天氣不錯想去爬山",
    ]

    index = load_keyword_index()
    if not index:
        print("keyword_index.json not found. Run pipeline.py first.")
    else:
        for text in test_inputs:
            result = match_user_input(text, index)
            print(f"Input: {text}")
            print(f"  Score: {result['match_score']}")
            print(f"  Has match: {result['has_match']}")
            print(f"  Categories: {list(result['matched_categories'].keys())}")
            if result["has_match"]:
                for cat, entries in result["matched_context"].items():
                    for e in entries:
                        print(f"    [{cat}] {e['title']}")
                        for t in e.get("scam_tactics", [])[:2]:
                            print(f"      -> {t}")
            print()
