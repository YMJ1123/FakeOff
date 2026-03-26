"""
Scam Pipeline 設定檔
Keywords, models, thresholds, and prompt templates.
"""

# ── Bedrock Model IDs ──────────────────────────────────────────────
LLM_MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
EMBED_TEXT_MODEL_ID = "amazon.titan-embed-text-v2:0"
EMBED_MULTIMODAL_MODEL_ID = "amazon.titan-embed-image-v1"
BEDROCK_REGION = "us-west-2"

# ── Embedding 設定 ─────────────────────────────────────────────────
EMBEDDING_DIMENSIONS = 1024

# ── Keyword 分類 ───────────────────────────────────────────────────
SCAM_KEYWORDS = {
    "time_pressure": {
        "weight": 2,
        "words": [
            "截止", "最後一天", "最後期限", "限時", "即將截止",
            "延長", "延期", "倒數", "儘速", "盡快", "本月底前",
            "逾期", "過期", "緊急", "立即",
        ],
    },
    "official_event": {
        "weight": 2,
        "words": [
            "報稅", "退稅", "補助", "津貼", "發放", "申請", "登記",
            "健保", "勞保", "國稅局", "財政部", "監理站", "戶政",
            "政府", "官方", "數位發展部", "憑證", "內政部", "衛福部",
        ],
    },
    "money_flow": {
        "weight": 2,
        "words": [
            "匯款", "轉帳", "退款", "繳費", "扣款", "入帳",
            "帳單", "信用卡", "銀行", "支付", "ATM", "款項",
            "刷卡", "金融卡",
        ],
    },
    "account_verify": {
        "weight": 2,
        "words": [
            "登入", "驗證", "身份確認", "帳號異常", "密碼",
            "OTP", "驗證碼", "更新資料", "個資", "重新登入",
            "認證", "實名制",
        ],
    },
    "hot_events": {
        "weight": 1,
        "words": [
            "地震", "颱風", "停電", "疫情", "疫苗", "補助",
            "演唱會", "中獎", "股東會", "報稅季", "開學", "購物節",
            "雙11", "黑色星期五", "選舉", "普發現金",
        ],
    },
    "delivery_channel": {
        "weight": 1,
        "words": [
            "簡訊", "email", "電子郵件", "通知", "連結",
            "網站", "官方網站", "申報網站", "下載", "APP",
            "LINE", "手機", "來電",
        ],
    },
}

# ── 風險門檻 ───────────────────────────────────────────────────────
SCORE_THRESHOLD_LOW = 2       # <= 2: 丟掉
SCORE_THRESHOLD_MEDIUM = 4    # 3-4: 進 LLM 二次判斷
                              # >= 5: 高潛力，直接進案例生成

# ── 新聞來源 RSS ───────────────────────────────────────────────────
NEWS_SOURCES = {
    "ltn": {
        "name": "自由時報",
        "rss": "https://news.ltn.com.tw/rss/all.xml",
        "type": "rss",
    },
    "ettoday": {
        "name": "ETtoday",
        "rss": "https://feeds.feedburner.com/ettoday/realtime",
        "type": "rss",
    },
    "yahoo_tw": {
        "name": "Yahoo新聞",
        "rss": "https://tw.news.yahoo.com/rss/",
        "type": "rss",
    },
    "setn": {
        "name": "三立新聞",
        "rss": "https://www.setn.com/rss.xml",
        "type": "rss",
        "needs_scrape_title": True,
    },
}

# ── 官方反詐來源 ───────────────────────────────────────────────────
OFFICIAL_SOURCES = [
    {"name": "165全民防騙", "url": "https://165.npa.gov.tw/"},
    {"name": "財政部", "url": "https://www.mof.gov.tw/"},
    {"name": "金管會", "url": "https://www.fsc.gov.tw/"},
]

# ── Prompt Templates ──────────────────────────────────────────────

ANALYSIS_PROMPT = """你是一個反詐騙事件分析器。

請根據下面這篇新聞，判斷它是否具有「可被詐騙集團利用」的空間。

請輸出 JSON，包含：
1. scam_potential: "low" / "medium" / "high"
2. reason: 為什麼這個事件容易被利用
3. impersonation_targets: 可能被冒充的單位或角色（list）
4. likely_channels: 可能使用的傳播方式（簡訊、email、電話、假網站、社群）（list）
5. likely_actions: 可能誘導使用者做的事（點連結、輸入個資、轉帳、登入）（list）
6. scam_angles: 2~5 個可能的詐騙切入角度（list）
7. seasonality: 是否具有時效性，若有請描述

只輸出合法 JSON，不要多餘文字。

新聞內容：
{article_text}"""

CASE_GENERATION_PROMPT = """你是一個反詐騙資料生成器。

請根據以下真實新聞事件與分析結果，生成 3 個「可能出現的時效性詐騙案例摘要」。

限制：
1. 不要生成可直接拿去害人的高擬真完整詐騙文案
2. 只輸出教育與訓練用途的案例摘要
3. 每個案例包含：
   - title: 案例標題
   - event_hook: 利用什麼事件切入
   - impersonated_entity: 冒充的對象
   - scam_goal: 詐騙目的
   - likely_channel: 傳播管道
   - red_flags: 辨識特徵（list）
   - safe_response: 正確應對方式

只輸出合法 JSON array，不要多餘文字。

新聞摘要：
{news_summary}

事件分析：
{analysis_json}"""

# ── SQLite 設定 ────────────────────────────────────────────────────
DB_PATH = "scam_pipeline.db"
