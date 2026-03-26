"""
LLM-based event analysis using Amazon Bedrock Converse API.
Determines whether a news event has scam exploitation potential.
"""

import json
import os

import boto3
from dotenv import load_dotenv

from config import ANALYSIS_PROMPT, BEDROCK_REGION, LLM_MODEL_ID

load_dotenv()
os.environ["AWS_BEARER_TOKEN_BEDROCK"] = os.getenv("API_KEY", "")

_client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)


def analyze_event(article_text: str) -> dict:
    """
    Send article text to LLM for scam-potential analysis.
    Returns parsed JSON dict with scam_potential, reason, etc.
    """
    prompt = ANALYSIS_PROMPT.format(article_text=article_text)

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
    """Extract JSON from LLM response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"scam_potential": "unknown", "reason": f"Failed to parse: {text[:200]}"}


if __name__ == "__main__":
    test_text = (
        "財政部宣布今年報稅截止日延長至6月底，國稅局提醒民眾儘速完成申報。"
        "民眾可透過官方網站或APP線上申報，完成後可查詢退稅進度。"
        "國稅局表示，逾期未申報者將依法處罰。"
    )
    result = analyze_event(test_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
