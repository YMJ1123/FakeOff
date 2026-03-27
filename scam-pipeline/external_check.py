"""
External fraud-detection API calls (AWS API Gateway).
  - URL risk check   (POST /url-check-cache → fallback /url-check)
  - Phone number check (GET /number-check/{country}/{number})

Rate limit: 1 RPS per endpoint, burst 2.
"""

import os
import re
import time
import urllib.parse

import requests
from dotenv import load_dotenv

load_dotenv()

_BASE = "https://hljaj2f6gf.execute-api.ap-northeast-1.amazonaws.com/prod"
_API_KEY = os.getenv("ANTI_FRAUD_API_KEY", "")
_HEADERS_JSON = {
    "x-api-key": _API_KEY,
    "Content-Type": "application/json",
}
_HEADERS_GET = {
    "x-api-key": _API_KEY,
}

_URL_RE = re.compile(
    r'https?://[^\s<>"\')\]]+|'
    r'(?<!\w)(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|tw|io|cc|me|co|info|biz|xyz)[^\s<>"\')\]]*',
    re.IGNORECASE,
)
_PHONE_RE = re.compile(
    r'\+?\d[\d\s\-()]{6,}\d'
)


def extract_urls(text: str) -> list[str]:
    return list(dict.fromkeys(_URL_RE.findall(text)))


def extract_phones(text: str) -> list[dict]:
    raw = _PHONE_RE.findall(text)
    results = []
    seen = set()
    for r in raw:
        digits = re.sub(r'[\s\-()]', '', r)
        if digits in seen:
            continue
        seen.add(digits)
        country = "TW"
        if digits.startswith("+886"):
            country = "TW"
        elif digits.startswith("+"):
            country = "US"
        results.append({"country": country, "number": digits})
    return results


def _normalize_url_result(raw: dict, url: str, source: str) -> dict:
    pd = raw.get("primarydomain", {})
    ap = raw.get("antiphishing", {})
    dns = raw.get("dnsblock", {})
    ident = raw.get("identifier", {})
    whois = raw.get("whois", {})
    reg = whois.get("registrant", {})

    return {
        "url": url,
        "domain": ident.get("host", url),
        "score": pd.get("score"),
        "blacklisted": raw.get("blacklisted", False),
        "phishing_count": ap.get("count", 0),
        "threat_count": dns.get("threat", {}).get("count", 0),
        "is_offline": raw.get("is_offline", False),
        "registrant": reg.get("company") or reg.get("name"),
        "country": reg.get("country"),
        "created": whois.get("registration_created"),
        "source": source,
    }


def check_url(url: str) -> dict:
    if not url.startswith("http"):
        url = "https://" + url
    try:
        resp = requests.post(
            f"{_BASE}/url-check-cache",
            json={"url": url},
            headers=_HEADERS_JSON,
            timeout=15,
        )
        if resp.status_code == 200:
            return _normalize_url_result(resp.json(), url, "url-check-cache")
    except Exception:
        pass

    time.sleep(1.2)

    try:
        resp = requests.post(
            f"{_BASE}/url-check",
            json={"url": url},
            headers=_HEADERS_JSON,
            timeout=30,
        )
        if resp.status_code == 200:
            return _normalize_url_result(resp.json(), url, "url-check")
        return {"url": url, "error": f"HTTP {resp.status_code}", "source": "url-check"}
    except Exception as e:
        return {"url": url, "error": str(e), "source": "url-check"}


def check_number(country: str, number: str) -> dict:
    encoded = urllib.parse.quote(number, safe="")
    try:
        resp = requests.get(
            f"{_BASE}/number-check/{country}/{encoded}",
            headers=_HEADERS_GET,
            timeout=15,
        )
        if resp.status_code == 200:
            raw = resp.json()
            inner = raw.get("data") or {}
            return {
                "number": number,
                "country": country,
                "name": inner.get("name"),
                "region": inner.get("region"),
                "spam_category": inner.get("spam_category"),
                "business_categories": inner.get("business_categories", []),
            }
        return {"number": number, "country": country, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"number": number, "country": country, "error": str(e)}


def check_urls(urls: list[str]) -> list[dict]:
    results = []
    for i, url in enumerate(urls[:5]):
        if i > 0:
            time.sleep(1.2)
        results.append(check_url(url))
    return results


def check_numbers(phones: list[dict]) -> list[dict]:
    results = []
    for i, p in enumerate(phones[:5]):
        if i > 0:
            time.sleep(1.2)
        results.append(check_number(p.get("country", "TW"), p["number"]))
    return results
