# 麥騙 FakeOff

Real-time AI-driven protection against phishing, scams, and malicious links.

## 專案結構

```
AWS_hackathon/
├── src/                        # 前端 React 應用程式原始碼
├── scam-pipeline/              # 詐騙案例自動生成 pipeline
│   ├── config.py               #   Keywords, model IDs, prompt templates
│   ├── crawler.py              #   RSS 新聞爬蟲
│   ├── event_filter.py         #   關鍵字篩選 & 風險評分
│   ├── analyzer.py             #   LLM 事件分析（Bedrock Converse）
│   ├── case_generator.py       #   生成教育用詐騙案例
│   ├── embedder.py             #   Titan Embedding 介面（備用）
│   ├── db.py                   #   SQLite schema & CRUD
│   ├── pipeline.py             #   主流程控制器
│   └── requirements.txt
├── api-key-test/               # Amazon Bedrock API 測試工具
│   ├── test_vlm.py             #   VLM 視覺語言模型測試
│   ├── test_text.py            #   純文字模型測試
│   └── test_embedding.py       #   Embedding 模型測試
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Scam Pipeline — 詐騙案例自動生成

從即時新聞中自動找出有詐騙利用空間的事件，透過 LLM 分析風險並生成教育用詐騙案例。

### Pipeline 流程

```
RSS 新聞爬蟲
  → 關鍵字篩選 & 風險評分
  → LLM 事件分析（判斷詐騙利用空間）
  → 生成教育用詐騙案例摘要
  → 存入 SQLite
```

### 新聞來源

| 來源 | 類型 |
|------|------|
| 自由時報 | RSS |
| ETtoday | RSS |
| Yahoo 新聞 | RSS |
| 三立新聞 | RSS（自動 scrape 標題） |

### 關鍵字風險評分

依 6 類關鍵字加權計分，篩選有詐騙利用空間的新聞：

- **時間壓力**（截止、限時、延長...）+2
- **政府/官方事件**（報稅、退稅、補助...）+2
- **金流相關**（匯款、轉帳、退款...）+2
- **帳號/驗證**（登入、驗證、OTP...）+2
- **高熱度事件**（地震、颱風、購物節...）+1
- **通知與連結**（簡訊、email、網站...）+1

Score >= 3 進入 LLM 分析，Score >= 5 為高風險。

### 前置需求

- Python 3
- Amazon Bedrock API Key

```bash
cd scam-pipeline
pip install -r requirements.txt
```

### 設定

在 `scam-pipeline/.env` 中設定 Bedrock API Key：

```
API_KEY=bedrock-api-key-xxxxxxx
```

### 執行

```bash
cd scam-pipeline

# Demo 模式（內建測試資料，不需爬蟲）
python pipeline.py demo

# Full 模式（爬取即時新聞 RSS）
python pipeline.py full
```

### 輸出

生成的案例存入 `scam_pipeline.db`（SQLite），每個案例包含：

- 標題 & 事件切入點
- 冒充對象 & 詐騙目的
- 傳播管道
- 辨識特徵（red flags）
- 正確應對方式

### 使用模型

| 用途 | Model ID |
|------|----------|
| 事件分析 & 案例生成 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| 文字 Embedding（備用）| `amazon.titan-embed-text-v2:0` |
| 多模態 Embedding（備用）| `amazon.titan-embed-image-v1` |

## 前端應用程式

**技術棧**：React 19 + TypeScript + Tailwind CSS 4 + Vite

```bash
npm install
npm run dev
```

應用程式會在 `http://localhost:3000` 啟動。

## API 測試工具

`api-key-test/` 資料夾包含獨立的 Bedrock API 測試腳本：

```bash
cd api-key-test

python test_vlm.py          # 圖片分析（Claude Haiku 4.5）
python test_text.py         # 純文字生成（Llama 3.3 70B）
python test_embedding.py    # Embedding 測試（Titan V2 + Multimodal）
```

## 注意事項

- API Key 為短期金鑰，僅供開發測試使用
- `.env` 檔案不應上傳至版本控制
- `scam-pipeline` 生成的案例僅供教育與訓練用途
