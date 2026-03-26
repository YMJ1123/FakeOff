"""
End-to-end test for the API server flow (text + screenshot paths).

Usage:
  python test_api_flow.py                              # default text test
  python test_api_flow.py --text "你收到的可疑訊息"
  python test_api_flow.py --image screenshot.png        # screenshot path
  python test_api_flow.py --image img.jpg --text "附帶文字"
  python test_api_flow.py --all                         # all text test cases
"""

import argparse
import base64
import json
import urllib.request
import urllib.error
from pathlib import Path

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


def format_vlm_result(text: str) -> dict:
    """Text-only path: format as same structure as VLM output."""
    return {
        "extracted_text": text,
        "urls": [],
        "phones": [],
        "image_type": None,
        "sender": None,
        "summary": text[:60] + "..." if len(text) > 60 else text,
    }


def run_test(text: str = None, image_path: str = None):
    has_screenshot = image_path is not None
    print(f"{'='*60}")
    print(f"Input type: {'Screenshot' + (' + Text' if text else '') if has_screenshot else 'Text'}")
    if text:
        print(f"Text: {text}")
    if image_path:
        print(f"Image: {image_path}")
    print(f"{'='*60}")

    # Step 0: VLM / Text normalization (unified format)
    if has_screenshot:
        print("\n[Step 0] VLM Screenshot Analysis (Sonnet)...")
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        vlm = call_api("/vlm-analyze", {"image_base64": b64})
        if "error" in vlm:
            print(f"  Error: {vlm['error']}")
            return
        combined_text = text + "\n\n[截圖內容]\n" + vlm["extracted_text"] if text else vlm["extracted_text"]
    else:
        vlm = format_vlm_result(text)
        combined_text = text

    print(f"  extracted_text: {vlm['extracted_text'][:80]}{'...' if len(vlm.get('extracted_text','')) > 80 else ''}")
    print(f"  image_type: {vlm.get('image_type')}")
    print(f"  sender: {vlm.get('sender')}")
    print(f"  urls: {vlm.get('urls', [])}")
    print(f"  phones: {vlm.get('phones', [])}")
    print(f"  summary: {vlm.get('summary')}")

    # Step 1: Keyword Check
    print("\n[Step 1] Keyword Check...")
    kw = call_api("/keyword-check", {"text": combined_text})
    print(f"  Has match: {kw['has_match']}")
    print(f"  Score: {kw['match_score']}")
    if kw["matched_categories"]:
        for cat, words in kw["matched_categories"].items():
            print(f"  [{cat}] → {', '.join(words)}")

    if not kw["has_match"] and not vlm.get("urls"):
        print("\n  → 未命中關鍵字且無 URL，跳過 Conclusion Agent")
        print()
        return

    # Step 2: Conclusion Agent
    print("\n[Step 2] Conclusion Agent...")
    conclusion = call_api("/conclude", {
        "user_input": combined_text,
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
    parser.add_argument("--image", type=str, default=None)
    parser.add_argument("--all", action="store_true", help="Run all text test cases")
    args = parser.parse_args()

    if args.image:
        run_test(text=args.text, image_path=args.image)
    elif args.text:
        run_test(text=args.text)
    elif args.all:
        for t in TEST_CASES:
            run_test(text=t)
    else:
        run_test(text=TEST_CASES[0])


if __name__ == "__main__":
    main()
