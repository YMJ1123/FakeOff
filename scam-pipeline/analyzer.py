"""
LLM-based scam tactics extraction using Amazon Bedrock Converse API.
For each news article, extract possible scam tactics in a lightweight format.
"""

import json
import os

import boto3
from dotenv import load_dotenv

from config import BEDROCK_REGION, LLM_MODEL_ID, TACTICS_PROMPT

load_dotenv()
os.environ["AWS_BEARER_TOKEN_BEDROCK"] = os.getenv("API_KEY", "")

_client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)


def extract_tactics(title: str, article_text: str) -> dict:
    """
    Extract scam tactics from a single news article.
    Returns: {scam_tactics: [...], impersonation_targets: [...], risk_level: str}
    """
    prompt = TACTICS_PROMPT.format(title=title, article_text=article_text[:3000])

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
        return {"scam_tactics": [], "impersonation_targets": [], "risk_level": "unknown"}


if __name__ == "__main__":
    result = extract_tactics(
        title="報稅截止日延長至6月底 國稅局提醒儘速完成申報",
        article_text="財政部宣布今年報稅截止日延長，民眾可透過官方網站或APP線上申報退稅。逾期未申報者將依法處罰。",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
