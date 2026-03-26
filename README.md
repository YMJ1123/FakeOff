# 麥騙 FakeOff

Real-time AI-driven protection against phishing, scams, and malicious links.

## 專案結構

```
AWS_hackathon/
├── src/                    # 前端 React 應用程式原始碼
├── api-key-test/           # Amazon Bedrock API 測試工具
│   ├── .env                # API Key 設定（勿上傳）
│   └── test_vlm.py         # VLM 視覺語言模型測試腳本
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 前端應用程式

**技術棧**：React 19 + TypeScript + Tailwind CSS 4 + Vite

### 本地執行

**前置需求**：Node.js

```bash
npm install
npm run dev
```

應用程式會在 `http://localhost:3000` 啟動。

## Amazon Bedrock API 測試（VLM）

使用 Amazon Bedrock Converse API 搭配 Claude Haiku 4.5 進行圖片分析測試。

### 前置需求

- Python 3
- boto3 SDK
- python-dotenv

```bash
pip install boto3 python-dotenv
```

### 設定

1. 在 `api-key-test/.env` 中設定你的 Bedrock API Key：

```
API_KEY=bedrock-api-key-xxxxxxx
```

2. 將要分析的圖片放入 `api-key-test/` 目錄

### 執行測試

```bash
cd api-key-test
python test_vlm.py
```

腳本會讀取圖片並透過 Claude Haiku 4.5 模型（`us.anthropic.claude-haiku-4-5-20251001-v1:0`）分析圖片內容。

### 注意事項

- 圖片格式需與腳本中的 `format` 參數一致（支援 `jpeg`、`png` 等）
- API Key 為短期金鑰，僅供開發測試使用
- `.env` 檔案不應上傳至版本控制
