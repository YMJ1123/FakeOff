"""
Flask API server exposing VLM, keyword_check, classifier, external checks,
and conclusion_agent as HTTP endpoints.

Endpoints:
  POST /vlm-analyze    — screenshot analysis (Sonnet VLM)
  POST /keyword-check  — match user text against keyword index
  POST /classify       — ML classifier scam detection (Scam Armor)
  POST /url-check      — external URL risk check (AWS API Gateway)
  POST /number-check   — external phone number check (AWS API Gateway)
  POST /conclude       — final scam judgment with all context
  GET  /news           — deduplicated news from keyword index
  POST /news/refresh   — re-crawl news and rebuild keyword index

Run:
  python api_server.py              # default port 5001
  python api_server.py --port 5002  # custom port
"""

import argparse
import json
import traceback

from flask import Flask, jsonify, request
from flask_cors import CORS

from conclusion_agent import judge_user_input
from external_check import check_numbers, check_url, check_urls, extract_phones, extract_urls
from keyword_check import (
    format_context_for_conclusion,
    load_keyword_index,
    match_user_input,
)
from scam_classifier import classify_text
from vlm_analyzer import analyze_screenshot_base64

app = Flask(__name__)
CORS(app)

_keyword_index = None


def get_keyword_index():
    global _keyword_index
    if _keyword_index is None:
        _keyword_index = load_keyword_index()
    return _keyword_index


def reload_keyword_index():
    global _keyword_index
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


@app.route("/classify", methods=["POST"])
def classify_endpoint():
    """
    Scam Armor — ML classifier for scam detection.
    Input:  {"text": "使用者收到的可疑訊息"}
    Output: {
        "label": "scam" | "legitimate",
        "confidence": 0.85,
        "scam_probability": 0.85,
        "legitimate_probability": 0.15
    }
    """
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "missing 'text' field"}), 400

    try:
        result = classify_text(text)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Classifier failed: {e}"}), 502

    return jsonify(result)


@app.route("/url-check", methods=["POST"])
def url_check_endpoint():
    """
    Check URL(s) against the external anti-fraud API.
    Input:  {"urls": ["https://example.com"]}
      or    {"text": "some text with urls"}
    Output: {"url_results": [{url, score, blacklisted, ...}]}
    """
    data = request.get_json(force=True)
    urls = data.get("urls", [])
    if not urls:
        text = data.get("text", "")
        if text:
            urls = extract_urls(text)
    if not urls:
        return jsonify({"url_results": [], "message": "no URLs found"})

    try:
        results = check_urls(urls)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"URL check failed: {e}"}), 502

    return jsonify({"url_results": results})


@app.route("/number-check", methods=["POST"])
def number_check_endpoint():
    """
    Check phone number(s) against the external anti-fraud API.
    Input:  {"phones": [{"country": "TW", "number": "+886..."}]}
      or    {"text": "some text with phone numbers"}
    Output: {"number_results": [{number, country, name, region, ...}]}
    """
    data = request.get_json(force=True)
    phones = data.get("phones", [])
    if not phones:
        text = data.get("text", "")
        if text:
            phones = extract_phones(text)
    if not phones:
        return jsonify({"number_results": [], "message": "no phone numbers found"})

    try:
        results = check_numbers(phones)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Number check failed: {e}"}), 502

    return jsonify({"number_results": results})


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
    classifier_result = data.get("classifier_result", {})
    url_results = data.get("url_results", [])
    number_results = data.get("number_results", [])

    context_payload = {
        "user_input": user_input,
        "match_score": keyword_match.get("match_score", 0),
        "matched_categories": keyword_match.get("matched_categories", {}),
        "matched_dynamic_keywords": keyword_match.get("matched_dynamic_keywords", []),
        "relevant_news_and_tactics": keyword_match.get("matched_context", {}),
        "classifier_result": classifier_result,
        "url_results": url_results,
        "number_results": number_results,
    }

    try:
        judgment = judge_user_input(context_payload)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"LLM call failed: {e}"}), 502

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

    try:
        result = analyze_screenshot_base64(b64)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"VLM call failed: {e}"}), 502

    return jsonify(result)


@app.route("/news", methods=["GET"])
def news_endpoint():
    """
    Return deduplicated news articles from keyword_index,
    grouped with their matched categories, sources, and scam tactics.
    """
    index = get_keyword_index()
    seen = {}
    for category, entries in index.items():
        for entry in entries:
            title = entry.get("title", "")
            if not title:
                continue
            if title not in seen:
                seen[title] = {
                    "title": title,
                    "url": entry.get("url", ""),
                    "source": entry.get("source", ""),
                    "published_at": entry.get("published_at", ""),
                    "risk_level": entry.get("risk_level", "unknown"),
                    "categories": [],
                    "scam_tactics": entry.get("scam_tactics", []),
                    "impersonation_targets": entry.get("impersonation_targets", []),
                }
            if category not in seen[title]["categories"]:
                seen[title]["categories"].append(category)

    articles = sorted(seen.values(), key=lambda x: len(x["categories"]), reverse=True)
    return jsonify({"articles": articles, "total": len(articles)})


@app.route("/news/refresh", methods=["POST"])
def news_refresh_endpoint():
    """
    Re-crawl news, filter, extract tactics, and rebuild keyword_index.json.
    Then reload the in-memory keyword index.
    """
    try:
        from pipeline import run_pipeline
        run_pipeline(max_per_source=25, fetch_full_text=False)
        idx = reload_keyword_index()
        return jsonify({
            "status": "ok",
            "categories": len(idx),
            "message": "News refreshed and keyword index rebuilt",
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Refresh failed: {e}"}), 502


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

    print(f"Loading scam classifier model...")
    try:
        from scam_classifier import _load_model
        _load_model()
        print("Classifier model loaded")
    except Exception as e:
        print(f"Warning: classifier model not loaded: {e}")

    print(f"Starting API server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)
