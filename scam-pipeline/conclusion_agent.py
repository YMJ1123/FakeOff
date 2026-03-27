"""
Conclusion agent:
  1. News-only mode: receives keyword-indexed data → comprehensive risk report
  2. User-query mode: receives user input + matched context → scam judgment for the user
"""

import json
import os

import boto3
from dotenv import load_dotenv

from config import BEDROCK_REGION, CONCLUSION_PROMPT, LLM_MODEL_ID

load_dotenv()
os.environ["AWS_BEARER_TOKEN_BEDROCK"] = os.getenv("API_KEY", "")

_client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

# User-facing conclusion prompt
USER_CONCLUSION_PROMPT = """你是麥騙 FakeOff 系統的反詐騙判斷助理。

使用者收到一則可疑訊息，請你根據以下資訊判斷這則訊息是否為詐騙。

## 使用者收到的訊息
{user_input}

## ML 分類器預判結果（Scam Armor）
{classifier_result}

## 關鍵字命中類別與命中詞
{matched_categories}

## 近期相關高風險新聞事件與已知詐騙手法
{relevant_context}

## 外部 API 查詢結果（URL 與電話）
{external_results}

---

請綜合以上所有資訊做出判斷。特別注意：
- ML 分類器的預判結果是一個重要的初始訊號，但不是最終判斷。請結合其他證據做出綜合判斷。
- 若 URL 查詢結果顯示高風險分數、黑名單、或釣魚記錄，應列為重要可疑特徵
- 若電話號碼被標記為 spam 或無法查到正當登記，也是可疑特徵
- 若關鍵字命中了近期的新聞詐騙手法，應交叉比對使用者收到的訊息

請輸出 JSON，包含：
1. is_scam: true / false / "uncertain"
2. confidence: 0.0 ~ 1.0
3. scam_type: 詐騙類型（如「假冒官方通知」「釣魚簡訊」「假客服電話」等，若非詐騙則為 null）
4. reasoning: 為什麼這樣判斷（一段話）
5. matched_news_event: 最相關的近期新聞事件（若有）
6. matched_tactic: 最吻合的已知詐騙手法（若有）
7. red_flags: 這則訊息中的可疑特徵（list）
8. advice: 給使用者的建議（一段話，用一般民眾看得懂的語言）

只輸出合法 JSON，不要多餘文字。"""


def run_conclusion(keyword_indexed_data: dict) -> dict:
    """News-only mode: feed keyword index → comprehensive risk report."""
    data_str = json.dumps(keyword_indexed_data, ensure_ascii=False, indent=2)
    prompt = CONCLUSION_PROMPT.format(keyword_indexed_data=data_str)
    return _call_llm(prompt)


def judge_user_input(context_payload: dict) -> dict:
    """
    User-query mode: judge whether the user's message is a scam.

    Args:
        context_payload: {
            "user_input": str,
            "match_score": int,
            "matched_categories": {cat: [words]},
            "relevant_news_and_tactics": {cat: [{title, scam_tactics, ...}]},
            "url_results": [{url, score, blacklisted, ...}],  (optional)
            "number_results": [{number, spam_category, ...}],  (optional)
        }
    """
    relevant_str = ""
    for cat, entries in context_payload.get("relevant_news_and_tactics", {}).items():
        relevant_str += f"\n### 類別: {cat}\n"
        for e in entries:
            relevant_str += f"- 新聞: {e['title']}\n"
            for t in e.get("scam_tactics", []):
                relevant_str += f"  - 已知手法: {t}\n"

    if not relevant_str:
        relevant_str = "（目前無近期相關高風險新聞事件）"

    categories_str = json.dumps(
        context_payload.get("matched_categories", {}),
        ensure_ascii=False, indent=2,
    )

    external_lines = []
    for u in context_payload.get("url_results", []):
        if u.get("score") is not None:
            external_lines.append(
                f"- URL {u.get('domain', u.get('url', '?'))}: "
                f"分數 {u['score']}/100, 黑名單={u.get('blacklisted')}, "
                f"釣魚記錄={u.get('phishing_count', 0)}, "
                f"威脅記錄={u.get('threat_count', 0)}"
            )
        elif u.get("error"):
            external_lines.append(f"- URL {u.get('url', '?')}: 查詢失敗 ({u['error']})")
    for n in context_payload.get("number_results", []):
        external_lines.append(
            f"- 電話 {n.get('number', '?')}: "
            f"登記名稱={n.get('name')}, 地區={n.get('region')}, "
            f"spam={n.get('spam_category')}"
        )
    external_str = "\n".join(external_lines) if external_lines else "（未偵測到 URL 或電話號碼，無外部查詢結果）"

    clf = context_payload.get("classifier_result", {})
    if clf:
        classifier_str = (
            f"預判標籤: {clf.get('label', 'N/A')}\n"
            f"詐騙機率: {clf.get('scam_probability', 'N/A')}\n"
            f"合法機率: {clf.get('legitimate_probability', 'N/A')}\n"
            f"信心度: {clf.get('confidence', 'N/A')}"
        )
    else:
        classifier_str = "（分類器未執行）"

    prompt = USER_CONCLUSION_PROMPT.format(
        user_input=context_payload["user_input"],
        classifier_result=classifier_str,
        matched_categories=categories_str,
        relevant_context=relevant_str,
        external_results=external_str,
    )
    return _call_llm(prompt)


def _call_llm(prompt: str) -> dict:
    response = _client.converse(
        modelId=LLM_MODEL_ID,
        messages=[{
            "role": "user",
            "content": [{"text": prompt}]
        }]
    )
    raw = response["output"]["message"]["content"][0]["text"]
    return _parse_json(raw)


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": f"Failed to parse: {text[:300]}"}
