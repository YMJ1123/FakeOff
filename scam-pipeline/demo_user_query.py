"""
End-to-end demo: simulates a user receiving a suspicious message.

Flow (matches architecture diagram):
  User input
    → keyword_check.match_user_input()     # "keyword check" box
    → keyword_check.format_context_for_conclusion()
    → conclusion_agent.judge_user_input()   # "Conclusion Agent" box
    → Final judgment for user
"""

import json

from keyword_check import format_context_for_conclusion, load_keyword_index, match_user_input
from conclusion_agent import judge_user_input


def judge(user_text: str, keyword_index: dict) -> dict:
    """Full chain: user input → keyword match → conclusion."""
    match_result = match_user_input(user_text, keyword_index)
    context = format_context_for_conclusion(user_text, match_result)
    judgment = judge_user_input(context)
    return {
        "input": user_text,
        "match_score": match_result["match_score"],
        "matched_categories": list(match_result["matched_categories"].keys()),
        "has_news_match": match_result["has_match"],
        "judgment": judgment,
    }


def main():
    index = load_keyword_index()
    if not index:
        print("keyword_index.json not found. Run `python pipeline.py demo` first.")
        return

    print(f"Loaded keyword_index with {len(index)} categories\n")

    test_messages = [
        "國稅局通知：您的退稅申請異常，請點擊以下連結重新驗證身份 https://tax-refund.tw.cc/verify",
        "【重要通知】您的銀行帳戶因系統升級需重新驗證，請立即登入 https://mybank-verify.com",
        "恭喜您獲得青創補助資格！請先繳交保證金3000元至以下帳戶以完成審核",
        "媽，我手機壞了，這是我的新號碼，可以先幫我轉5000元嗎？",
        "明天下午三點開會，請準時出席",
    ]

    for msg in test_messages:
        print("=" * 70)
        print(f"USER INPUT: {msg}")
        print("=" * 70)

        result = judge(msg, index)

        print(f"  Match score: {result['match_score']}")
        print(f"  Categories: {result['matched_categories']}")
        print(f"  News match: {result['has_news_match']}")

        j = result["judgment"]
        print(f"\n  JUDGMENT:")
        print(f"    Is scam:    {j.get('is_scam')}")
        print(f"    Confidence: {j.get('confidence')}")
        print(f"    Scam type:  {j.get('scam_type')}")
        print(f"    Reasoning:  {j.get('reasoning', '')[:100]}...")

        if j.get("matched_news_event"):
            print(f"    News event: {j['matched_news_event']}")
        if j.get("matched_tactic"):
            print(f"    Tactic:     {j['matched_tactic']}")

        flags = j.get("red_flags", [])
        if flags:
            print(f"    Red flags:")
            for f in flags:
                print(f"      - {f}")

        print(f"    Advice:     {j.get('advice', '')[:120]}...")
        print()


if __name__ == "__main__":
    main()
