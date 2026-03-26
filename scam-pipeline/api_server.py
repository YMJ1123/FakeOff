"""
Flask API server exposing VLM, keyword_check, and conclusion_agent
as HTTP endpoints for the n8n workflow.

Endpoints:
  POST /vlm-analyze    — screenshot analysis (Sonnet VLM)
  POST /keyword-check  — match user text against keyword index
  POST /conclude       — final scam judgment with all context

Run:
  python api_server.py              # default port 5001
  python api_server.py --port 5002  # custom port
"""

import argparse
import json

from flask import Flask, jsonify, request

from conclusion_agent import judge_user_input
from keyword_check import (
    format_context_for_conclusion,
    load_keyword_index,
    match_user_input,
)
from vlm_analyzer import analyze_screenshot_base64

app = Flask(__name__)

_keyword_index = None


def get_keyword_index():
    global _keyword_index
    if _keyword_index is None:
        _keyword_index = load_keyword_index()
    return _keyword_index


@app.route("/keyword-check", methods=["POST"])
def keyword_check_endpoint():
    """
    Input:  {"text": "使用者收到的可疑訊息"}
    Output: {
        "matched_categories": {"official_event": ["報稅", ...], ...},
        "matched_context":    {category: [{title, scam_tactics, ...}]},
        "match_score": 5,
        "has_match": true
    }
    """
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "missing 'text' field"}), 400

    index = get_keyword_index()
    result = match_user_input(text, index)
    return jsonify(result)


@app.route("/conclude", methods=["POST"])
def conclude_endpoint():
    """
    Input: {
        "user_input": "原始使用者訊息",
        "keyword_match": { ... from /keyword-check ... },
        "url_results": [ ... from anti-fraud url-check ... ],
        "number_results": [ ... from anti-fraud number-check ... ]
    }
    Output: {
        "is_scam": true,
        "confidence": 0.95,
        "scam_type": "假冒官方通知",
        "reasoning": "...",
        "red_flags": [...],
        "advice": "..."
    }
    """
    data = request.get_json(force=True)
    user_input = data.get("user_input", "")
    if not user_input:
        return jsonify({"error": "missing 'user_input' field"}), 400

    keyword_match = data.get("keyword_match", {})
    url_results = data.get("url_results", [])
    number_results = data.get("number_results", [])

    context_payload = {
        "user_input": user_input,
        "match_score": keyword_match.get("match_score", 0),
        "matched_categories": keyword_match.get("matched_categories", {}),
        "relevant_news_and_tactics": keyword_match.get("matched_context", {}),
        "url_results": url_results,
        "number_results": number_results,
    }

    judgment = judge_user_input(context_payload)
    return jsonify(judgment)


@app.route("/vlm-analyze", methods=["POST"])
def vlm_analyze_endpoint():
    """
    Input:  {"image_base64": "base64-encoded image data"}
    Output: {
        "extracted_text": "圖片主要區域的文字",
        "urls": ["https://..."],
        "phones": [{"country": "TW", "number": "+886..."}],
        "image_type": "sms",
        "sender": "發送者或來源",
        "summary": "客觀描述圖片內容"
    }
    """
    data = request.get_json(force=True)
    b64 = data.get("image_base64", "")
    if not b64:
        return jsonify({"error": "missing 'image_base64' field"}), 400

    result = analyze_screenshot_base64(b64)
    return jsonify(result)


@app.route("/health", methods=["GET"])
def health():
    index = get_keyword_index()
    return jsonify({
        "status": "ok",
        "keyword_index_categories": len(index),
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    print(f"Loading keyword index...")
    idx = get_keyword_index()
    print(f"Loaded {len(idx)} categories")
    print(f"Starting API server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)
