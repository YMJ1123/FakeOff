# 麥騙 FakeOff

Real-time AI-driven protection against phishing, scams, and malicious links.

## 系統架構

```
使用者輸入（Discord / Web）
  │
  ▼
┌─────────────────────────────────────────────────┐
│  n8n Workflow (Anti-Fraud LLM Router)           │
│                                                 │
│  Webhook Trigger                                │
│    → LLM Router (Bedrock Claude Haiku)          │
│        提取 URL / 電話號碼                        │
│    → Call Anti-Fraud APIs                       │
│        URL 風險查詢 / 電話號碼查詢                  │
│    → Keyword Check  ←── scam-pipeline API       │
│        關鍵字匹配近期高風險新聞                      │
│    → Conclusion Agent  ←── scam-pipeline API    │
│        AI 綜合判斷（詐騙/安全）                     │
│    → Respond to Webhook                         │
└─────────────────────────────────────────────────┘
  │                            ▲
  ▼                            │
Discord Bot / Web UI      scam-pipeline API Server
                          (Flask, port 5001)
                               ▲
                               │
                    ┌──────────┴──────────┐
                    │  Scam Pipeline      │
                    │  (定時執行)           │
                    │                     │
                    │  RSS 新聞爬蟲        │
                    │   → 關鍵字篩選       │
                    │   → LLM 手法分析     │
                    │   → 建立關鍵字索引    │
                    │   → Conclusion 報告  │
                    └─────────────────────┘
```

## 專案結構

```
AWS_hackathon/
├── scam-pipeline/              # 詐騙偵測核心 pipeline + API
│   ├── config.py               #   Keywords, model IDs, prompt templates
│   ├── crawler.py              #   RSS 新聞爬蟲
│   ├── event_filter.py         #   關鍵字篩選 & 風險評分
│   ├── analyzer.py             #   LLM 手法分析（Bedrock Converse）
│   ├── keyword_check.py        #   使用者輸入 ↔ 關鍵字索引匹配
│   ├── conclusion_agent.py     #   AI 總結判斷（新聞報告 / 使用者查詢）
│   ├── api_server.py           #   Flask API（/keyword-check, /conclude）
│   ├── llm_router.py           #   Bedrock LLM Router（提取 URL/電話）
│   ├── pipeline.py             #   主流程控制器
│   ├── demo_user_query.py      #   使用者查詢 demo
│   ├── test_api_flow.py        #   API 端到端測試
│   ├── case_generator.py       #   生成教育用詐騙案例（備用）
│   ├── embedder.py             #   Titan Embedding 介面（備用）
│   ├── db.py                   #   SQLite schema & CRUD
│   └── requirements.txt
├── api-key-test/               # Amazon Bedrock API 測試工具
│   ├── test_vlm.py             #   VLM 視覺語言模型測試
│   ├── test_text.py            #   純文字模型測試
│   └── test_embedding.py       #   Embedding 模型測試
├── src/                        # 前端 React 應用程式原始碼
├── requirements.txt            # Python 整體依賴
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 核心流程

### 1. Scam Pipeline — 新聞爬取 & 關鍵字索引建立

```
RSS 新聞爬蟲（自由時報、ETtoday、Yahoo、三立）
  → 關鍵字篩選 & 風險評分（6 類加權）
  → LLM 手法分析（每篇高風險新聞 → 詐騙手法 + 冒充對象）
  → 建立 keyword_index.json（按關鍵字類別索引）
  → Conclusion Agent 產出整體風險報告
```

### 2. API Server — 即時查詢服務

Flask server 暴露兩個 endpoint 給 n8n workflow 呼叫：

| Endpoint | Method | 說明 |
|---|---|---|
| `POST /keyword-check` | POST | 匹配使用者文字 → 返回命中類別、相關新聞事件 |
| `POST /conclude` | POST | 綜合所有資訊 → AI 詐騙判斷 |
| `GET /health` | GET | 服務狀態 |

### 3. n8n Workflow — 完整反詐流程

6 個節點串聯：

1. **Webhook Trigger** — 接收 Discord / Web 送來的使用者訊息
2. **LLM Router (Bedrock)** — 用 Claude Haiku 提取 URL 和電話號碼
3. **Call APIs and Merge** — 查詢外部反詐 API（URL 風險評分、電話號碼查詢）
4. **Keyword Check** — 呼叫 `scam-pipeline` API 匹配關鍵字索引
5. **Conclusion Agent** — 呼叫 `scam-pipeline` API 做 AI 最終判斷
6. **Respond to Webhook** — 回傳完整防詐分析報告

## 新聞來源

| 來源 | 類型 |
|------|------|
| 自由時報 | RSS |
| ETtoday | RSS |
| Yahoo 新聞 | RSS |
| 三立新聞 | RSS（自動 scrape 標題） |

## 關鍵字風險評分

依 6 類關鍵字加權計分，篩選有詐騙利用空間的新聞：

- **時間壓力**（截止、限時、延長...）+2
- **政府/官方事件**（報稅、退稅、補助...）+2
- **金流相關**（匯款、轉帳、退款...）+2
- **帳號/驗證**（登入、驗證、OTP...）+2
- **高熱度事件**（地震、颱風、購物節...）+1
- **通知與連結**（簡訊、email、網站...）+1

Score >= 3 進入 LLM 分析，Score >= 5 為高風險。

## 使用模型

| 用途 | Model ID |
|------|----------|
| LLM Router / 手法分析 / 總結判斷 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| 純文字測試 | `us.meta.llama3-3-70b-instruct-v1:0` |
| 文字 Embedding（備用）| `amazon.titan-embed-text-v2:0` |
| 多模態 Embedding（備用）| `amazon.titan-embed-image-v1` |

## 快速開始

### 前置需求

- Python 3.10+
- Node.js 20+（前端 & n8n）
- Amazon Bedrock API Key

### 安裝

```bash
# Python 依賴
pip install -r requirements.txt

# 前端依賴
npm install
```

### 設定環境變數

在 `scam-pipeline/.env` 中設定：

```
API_KEY=bedrock-api-key-xxxxxxx
```

### 執行 Pipeline（建立關鍵字索引）

```bash
cd scam-pipeline

# Demo 模式（內建測試資料，不需爬蟲）
python pipeline.py demo

# Full 模式（爬取即時新聞 RSS）
python pipeline.py full
```

產出：`keyword_index.json`（關鍵字索引）、`conclusion.json`（風險報告）

### 啟動 API Server

```bash
cd scam-pipeline
python api_server.py --port 5001
```

### 測試 API

```bash
cd scam-pipeline

# 測試完整 API 流程（keyword check → conclusion）
python test_api_flow.py --all

# 自訂文字測試
python test_api_flow.py --text "收到簡訊說銀行帳戶異常要轉帳"
```

### 啟動前端

```bash
npm run dev
```

應用程式會在 `http://localhost:3000` 啟動。

### n8n Workflow + Discord Bot

n8n workflow 和 Discord bot 位於獨立 repo：[scam_detection_n8n](https://github.com/YMJ1123/scam_detection_n8n)

#### 1. Clone n8n repo

```bash
git clone https://github.com/YMJ1123/scam_detection_n8n.git
cd scam_detection_n8n
cp .env.sample .env
```

編輯 `.env`，填入 API keys：

```
ANTI_FRAUD_API_KEY=your-anti-fraud-api-key
BEDROCK_API_KEY=your-bedrock-api-key
DISCORD_BOT_TOKEN=your-discord-bot-token
N8N_WEBHOOK_URL=http://localhost:5678/webhook/anti-fraud
```

#### 2. 啟動 n8n + Discord Bot（Docker Compose）

```bash
docker-compose up -d
```

這會啟動：
- **n8n** on `http://localhost:5678`
- **Discord Bot** 自動連線 Discord

#### 3. 匯入 Workflow

1. 開啟 `http://localhost:5678`
2. Create new workflow → **Import from File** → 選 `n8n_workflow.json`
3. **啟動 workflow**（右上角 Active 開關打開）

#### 4. 連接 scam-pipeline API Server

n8n workflow 中的 **Keyword Check** 和 **Conclusion Agent** 節點會呼叫 scam-pipeline 的 API server。

由於 n8n 跑在 Docker 容器中，`localhost` 指向容器自己，需要用 Docker bridge IP 才能打到主機：

```bash
# 查詢 Docker bridge IP（通常是 172.x.0.1）
ip addr show | grep 'inet 172\.'

# 確認 API server 可從該 IP 存取
curl http://172.19.0.1:5001/health
```

然後在 n8n 的 **Keyword Check** 和 **Conclusion Agent** Code 節點中，將 `PIPELINE_API` 設定為：

```javascript
const PIPELINE_API = 'http://172.19.0.1:5001';  // 換成你的 Docker bridge IP
```

#### 5. 測試

```bash
# 確保 scam-pipeline API server 正在運行
cd /path/to/FakeOff/scam-pipeline
python api_server.py --port 5001

# 在 scam_detection_n8n 目錄測試
cd /path/to/scam_detection_n8n
python test_webhook.py --text "我收到國稅局簡訊說要退稅，要點連結輸入銀行帳號"
```

#### 完整 n8n 節點流程

```
Webhook Trigger
  → LLM Router (Bedrock)        提取 URL / 電話號碼
  → Call APIs and Merge          查詢外部反詐 API
  → Keyword Check                匹配關鍵字索引（scam-pipeline API）
  → Conclusion Agent             AI 綜合判斷（scam-pipeline API）
  → Respond to Webhook           回傳防詐分析報告
```

## API 測試工具

`api-key-test/` 資料夾包含獨立的 Bedrock API 測試腳本：

```bash
cd api-key-test

python test_vlm.py          # 圖片分析（Claude Haiku 4.5）
python test_text.py         # 純文字生成（Llama 3.3 70B）
python test_embedding.py    # Embedding 測試（Titan V2 + Multimodal）
```

## 相關 Repo

| Repo | 說明 |
|------|------|
| [FakeOff](https://github.com/YMJ1123/FakeOff) | 主專案：前端 + scam-pipeline + API server |
| [scam_detection_n8n](https://github.com/YMJ1123/scam_detection_n8n) | n8n workflow + Discord bot + 反詐 API 整合 |

## 注意事項

- API Key 為短期金鑰，僅供開發測試使用
- `.env` 檔案不應上傳至版本控制
- `scam-pipeline` 生成的分析結果僅供教育與訓練用途
- n8n 在 Docker 容器中運行時，API Server 地址需使用 Docker bridge IP（如 `172.19.0.1`）
