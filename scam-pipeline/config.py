"""
Scam Pipeline 設定檔
Keywords, models, thresholds, and prompt templates.
"""

# ── Bedrock Model IDs ──────────────────────────────────────────────
LLM_MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
VLM_MODEL_ID = "us.anthropic.claude-sonnet-4-6"
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
SCORE_THRESHOLD_LOW = 0       # <= 0: 丟掉 (任何有命中就保留)
SCORE_THRESHOLD_MEDIUM = 3    # 1-3: 進 LLM 二次判斷
                              # >= 4: 高潛力，直接進案例生成

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

# Step 1: 針對單篇新聞，快速擷取可能的詐騙手法
TACTICS_PROMPT = """你是一個反詐騙事件分析器。

請根據以下新聞，簡要列出詐騙集團可能利用這則新聞的手法。

請輸出 JSON，包含：
1. scam_tactics: 2~4 個可能的詐騙手法（每個是一句話的描述）（list of strings）
2. impersonation_targets: 可能被冒充的單位或角色（list of strings）
3. risk_level: "low" / "medium" / "high"
4. keywords: 5~10 個可能出現在相關詐騙訊息中的關鍵字或短語（list of strings）。這些關鍵字應該是詐騙者在利用這則新聞進行詐騙時，受害者可能在訊息中看到的字詞，例如具體的機構名稱、政策名稱、操作指令、專有名詞等。

只輸出合法 JSON，不要多餘文字。

新聞標題：{title}
新聞內容：{article_text}"""

# Step 2: 結論模型，接收所有 keyword-indexed 資料做最終綜合判斷
CONCLUSION_PROMPT = """你是麥騙 FakeOff 系統的反詐騙總結分析師。

以下是我們從即時新聞中依「關鍵字類別」整理出的高風險事件與可能詐騙手法。
每個類別底下有多則新聞標題以及對應的詐騙手法。

請你做最終綜合判斷，輸出 JSON，包含：

1. high_alert_events: 當前最需要警示大眾的事件列表，每個事件包含：
   - event: 事件名稱（來自新聞標題）
   - keyword_categories: 涉及的關鍵字類別（list）
   - primary_scam_tactic: 最主要的詐騙手法（一句話）
   - target_audience: 最可能被騙的對象
   - urgency: "immediate" / "watch" / "low"
2. cross_event_patterns: 跨事件觀察到的共同詐騙模式（list of strings）
3. recommended_alerts: 建議對外發布的警示訊息（list of strings, 2~3 則，用一般民眾看得懂的語言）
4. summary: 整體詐騙風險摘要（一段話）

只輸出合法 JSON，不要多餘文字。

關鍵字分類資料：
{keyword_indexed_data}"""

# ── SQLite 設定 ────────────────────────────────────────────────────
DB_PATH = "scam_pipeline.db"
