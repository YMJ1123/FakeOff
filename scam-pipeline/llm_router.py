"""
LLM Router — replaces Groq LLM in n8n workflow.
Uses AWS Bedrock to extract URLs, phone numbers from user text.
This is the "function calling agent" in the architecture diagram.
"""

import json
import os
import re

import boto3
from dotenv import load_dotenv

from config import BEDROCK_REGION, LLM_MODEL_ID

load_dotenv()
os.environ["AWS_BEARER_TOKEN_BEDROCK"] = os.getenv("API_KEY", "")

_client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

ROUTER_SYSTEM_PROMPT = """You are an anti-fraud analysis router. Analyze the user's message and extract:
1. Any URLs (http://, https://, or bare domains like example.com)
2. Any phone numbers (any format: +886..., 09..., 02-xxxx-xxxx, etc.)

Return ONLY valid JSON:
{
  "urls": ["https://example.com"],
  "phones": [{"country": "TW", "number": "+886289667000"}],
  "has_text_content": true,
  "summary": "brief description of what was found"
}

Rules:
- For Taiwan numbers without country code (e.g. 0289667000, 09xx), remove leading 0, prepend +886, set country to "TW"
- For URLs without protocol, prepend https://
- has_text_content: true if the message contains suspicious text worth analyzing beyond URLs/phones
- If nothing is found, return empty arrays
- ONLY return the JSON object, no markdown, no explanation"""


def route(user_text: str) -> dict:
    """
    Extract URLs, phone numbers, and flags from user text using Bedrock LLM.
    Returns: {urls, phones, has_text_content, summary}
    """
    response = _client.converse(
        modelId=LLM_MODEL_ID,
        messages=[{
            "role": "user",
            "content": [{"text": user_text}]
        }],
        system=[{"text": ROUTER_SYSTEM_PROMPT}],
    )

    raw = response["output"]["message"]["content"][0]["text"]
    parsed = _parse_json(raw)

    parsed.setdefault("urls", [])
    parsed.setdefault("phones", [])
    parsed.setdefault("has_text_content", True)
    parsed.setdefault("summary", "")

    return parsed


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"urls": [], "phones": [], "has_text_content": True,
                "summary": f"Parse error: {text[:200]}"}


if __name__ == "__main__":
    test_cases = [
        "我收到一封信叫我去 https://tax-refund.tw.cc/verify 登入，還有人用 0912345678 打來說是國稅局",
        "收到簡訊說我中獎了，要我打 0289667000 或上 https://aws.amazon.com 領獎",
        "有人說可以幫我加速青創補助審核，要先繳保證金",
        "今天天氣真好",
    ]

    for text in test_cases:
        print(f"Input: {text}")
        result = route(text)
        print(f"  URLs:   {result['urls']}")
        print(f"  Phones: {result['phones']}")
        print(f"  Text:   {result['has_text_content']}")
        print(f"  Summary: {result['summary']}")
        print()
