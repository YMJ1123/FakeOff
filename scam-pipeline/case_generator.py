"""
Generate educational scam case summaries from analyzed news events.
Uses Bedrock Converse API with structured prompt.
"""

import json
import os

import boto3
from dotenv import load_dotenv

from config import BEDROCK_REGION, CASE_GENERATION_PROMPT, LLM_MODEL_ID

load_dotenv()
os.environ["AWS_BEARER_TOKEN_BEDROCK"] = os.getenv("API_KEY", "")

_client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)


def generate_cases(news_summary: str, analysis: dict) -> list[dict]:
    """
    Generate 3 educational scam case summaries based on
    a news event and its scam-potential analysis.
    """
    prompt = CASE_GENERATION_PROMPT.format(
        news_summary=news_summary,
        analysis_json=json.dumps(analysis, ensure_ascii=False, indent=2),
    )

    response = _client.converse(
        modelId=LLM_MODEL_ID,
        messages=[{
            "role": "user",
            "content": [{"text": prompt}]
        }]
    )

    raw = response["output"]["message"]["content"][0]["text"]
    return _parse_json_list(raw)


def _parse_json_list(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
        return [result]
    except json.JSONDecodeError:
        return [{"title": "Parse Error", "event_hook": text[:200]}]


if __name__ == "__main__":
    test_summary = "財政部宣布報稅截止日延長至6月底，民眾可透過官方網站申報退稅。"
    test_analysis = {
        "scam_potential": "high",
        "reason": "報稅季搭配退稅流程容易被冒用",
        "impersonation_targets": ["國稅局", "財政部"],
        "likely_channels": ["簡訊", "電子郵件", "假網站"],
        "likely_actions": ["點擊連結", "輸入個資"],
        "scam_angles": ["假退稅通知", "假申報網站"],
        "seasonality": "報稅季（5-6月）",
    }
    cases = generate_cases(test_summary, test_analysis)
    print(json.dumps(cases, ensure_ascii=False, indent=2))
