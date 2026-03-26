"""
End-to-end test for the API server flow:
  1. /keyword-check → match user text
  2. /conclude     → AI scam judgment

Usage:
  python test_api_flow.py
  python test_api_flow.py --text "你收到的可疑訊息"
"""

import argparse
import json
import urllib.request
import urllib.error

API_BASE = "http://localhost:5001"

TEST_CASES = [
    "我收到國稅局的簡訊說要退稅，要我點連結輸入銀行帳號",
    "有人打電話來說我的銀行帳戶異常，要我轉帳到安全帳戶",
    "收到 LINE 訊息說可以投資加密貨幣，報酬率 30%，加 LINE 群組",
    "今天天氣真好，適合出去走走",
]


def call_api(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_test(text: str):
    print(f"{'='*60}")
    print(f"Input: {text}")
    print(f"{'='*60}")

    print("\n[Step 1] Keyword Check...")
    kw = call_api("/keyword-check", {"text": text})
    print(f"  Has match: {kw['has_match']}")
    print(f"  Score: {kw['match_score']}")
    if kw["matched_categories"]:
        for cat, words in kw["matched_categories"].items():
            print(f"  [{cat}] → {', '.join(words)}")

    if not kw["has_match"]:
        print("\n  → 未命中任何高風險關鍵字，跳過 Conclusion Agent")
        print()
        return

    print("\n[Step 2] Conclusion Agent...")
    conclusion = call_api("/conclude", {
        "user_input": text,
        "keyword_match": kw,
        "url_results": [],
        "number_results": [],
    })

    if "error" in conclusion:
        print(f"  Error: {conclusion['error']}")
    else:
        scam_label = {True: "高度可疑詐騙", False: "看起來安全"}.get(
            conclusion.get("is_scam"), "無法確定"
        )
        conf = conclusion.get("confidence", 0)
        print(f"  判定: {scam_label}")
        print(f"  信心度: {round(conf * 100)}%")
        if conclusion.get("scam_type"):
            print(f"  詐騙類型: {conclusion['scam_type']}")
        print(f"  分析: {conclusion.get('reasoning', '')}")
        if conclusion.get("red_flags"):
            print(f"  可疑特徵:")
            for rf in conclusion["red_flags"]:
                print(f"    - {rf}")
        if conclusion.get("matched_news_event"):
            print(f"  相關新聞: {conclusion['matched_news_event']}")
        if conclusion.get("matched_tactic"):
            print(f"  吻合手法: {conclusion['matched_tactic']}")
        print(f"  建議: {conclusion.get('advice', '')}")
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, default=None)
    parser.add_argument("--all", action="store_true", help="Run all test cases")
    args = parser.parse_args()

    if args.text:
        run_test(args.text)
    elif args.all:
        for t in TEST_CASES:
            run_test(t)
    else:
        run_test(TEST_CASES[0])


if __name__ == "__main__":
    main()
