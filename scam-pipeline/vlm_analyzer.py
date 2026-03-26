"""
VLM Screenshot Analyzer — extracts text, URLs, phone numbers from images.

Uses Claude Sonnet (frozen) as the Light-Weight VLM.
This is the first step for screenshot inputs before they enter
the function calling agent pipeline.
"""

import base64
import json
import os
import re
from pathlib import Path

import boto3
from dotenv import load_dotenv

from config import BEDROCK_REGION, VLM_MODEL_ID

load_dotenv()
os.environ["AWS_BEARER_TOKEN_BEDROCK"] = os.getenv("API_KEY", "")

_client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

VLM_SYSTEM_PROMPT = """你是一個圖片文字提取工具。你的任務是客觀地讀取圖片內容，不做任何主觀判斷。

請仔細觀察這張圖片，提取以下資訊：

1. extracted_text: 圖片主要區域中可見的文字內容（忽略導覽列、狀態列等雜訊，聚焦在主要內容區域）
2. urls: 圖片中出現的所有網址（list of strings）
3. phones: 圖片中出現的所有電話號碼，每個包含 country 和 number（list of objects）
4. image_type: 圖片類型，如 "sms"、"email"、"website"、"chat"、"notification"、"ad"、"other"
5. sender: 訊息的發送者或來源（如有）
6. summary: 一句話客觀描述這張圖片呈現的內容（不做風險判斷）

注意：
- 只提取你在圖片中實際看到的資訊
- 不要加入任何主觀判斷或風險評估
- 忽略手機狀態列、導覽列等非主要內容
- 如果文字模糊不清，標記為 [模糊]

只輸出合法 JSON，不要多餘文字。"""


def analyze_screenshot(image_bytes: bytes, image_format: str = "png") -> dict:
    """
    Analyze a screenshot using VLM and extract structured information.

    Args:
        image_bytes: raw bytes of the image
        image_format: "png", "jpeg", "gif", or "webp"

    Returns:
        {extracted_text, urls, phones, image_type, sender, summary}
    """
    fmt = image_format.lower().replace("jpg", "jpeg")

    response = _client.converse(
        modelId=VLM_MODEL_ID,
        system=[{"text": VLM_SYSTEM_PROMPT}],
        messages=[{
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": fmt,
                        "source": {"bytes": image_bytes},
                    }
                },
                {"text": "請分析這張截圖。"},
            ],
        }],
    )

    raw = response["output"]["message"]["content"][0]["text"]
    return _parse_json(raw)


def analyze_screenshot_base64(b64_string: str) -> dict:
    """
    Analyze a base64-encoded screenshot.
    Auto-detects image format from the data or defaults to png.
    """
    if "," in b64_string:
        header, b64_data = b64_string.split(",", 1)
        if "jpeg" in header or "jpg" in header:
            fmt = "jpeg"
        elif "gif" in header:
            fmt = "gif"
        elif "webp" in header:
            fmt = "webp"
        else:
            fmt = "png"
    else:
        b64_data = b64_string
        fmt = _detect_format(b64_string)

    image_bytes = base64.b64decode(b64_data)
    return analyze_screenshot(image_bytes, fmt)


def _detect_format(b64_string: str) -> str:
    """Detect image format from the first few bytes."""
    try:
        header_bytes = base64.b64decode(b64_string[:32])
        if header_bytes[:3] == b"\xff\xd8\xff":
            return "jpeg"
        if header_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            return "png"
        if header_bytes[:4] == b"GIF8":
            return "gif"
        if header_bytes[:4] == b"RIFF" and header_bytes[8:12] == b"WEBP":
            return "webp"
    except Exception:
        pass
    return "png"


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": f"Failed to parse VLM response", "raw": text[:500]}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python vlm_analyzer.py <image_path>")
        sys.exit(1)

    img_path = Path(sys.argv[1])
    if not img_path.exists():
        print(f"File not found: {img_path}")
        sys.exit(1)

    suffix = img_path.suffix.lower().lstrip(".")
    with open(img_path, "rb") as f:
        result = analyze_screenshot(f.read(), suffix or "png")

    print(json.dumps(result, ensure_ascii=False, indent=2))
