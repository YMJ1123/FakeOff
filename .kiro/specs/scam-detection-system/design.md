# Design Document: Scam Detection System

## Overview

The Scam Detection System (麥騙 FakeOff) is a comprehensive AI-driven platform that combines multiple analysis techniques to detect phishing, scams, and malicious communications. The system integrates:

- **Neural network classification** for embedding-based scam detection
- **LLM-based reasoning** for contextual analysis and judgment
- **Visual Language Model (VLM)** for screenshot analysis
- **Real-time news monitoring** to maintain current scam intelligence
- **Keyword-based risk scoring** for pattern matching
- **External API integration** for URL and phone number verification

The system serves end users through a React-based web interface and provides REST API endpoints for integration with external platforms (Discord bots, n8n workflows, etc.).

### Key Design Principles

1. **Multi-layered detection**: Combine multiple detection methods (ML classifier, keyword matching, LLM reasoning) for robust scam identification
2. **Real-time intelligence**: Continuously update knowledge base from news sources to stay current with evolving scam tactics
3. **Explainability**: Provide clear reasoning and red flags to help users understand why something is flagged as a scam
4. **Resilience**: Gracefully handle API failures, missing data, and edge cases without breaking the user experience
5. **Modularity**: Separate concerns (crawler, classifier, API, frontend) for independent development and testing

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  - User input interface (text/screenshot)                    │
│  - Analysis result display                                   │
│  - History and blacklist views                               │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Server (Flask)                         │
│  - /keyword-check: Match user input to scam patterns        │
│  - /conclude: Final scam judgment                            │
│  - /vlm-analyze: Screenshot analysis                         │
│  - /health: Service status                                   │
└─────┬───────────────────────┬───────────────────────────────┘
      │                       │
      ▼                       ▼
┌─────────────────────┐         ┌──────────────────────────────┐
│  Keyword Index      │         │   Amazon Bedrock Services    │
│  (keyword_index.json)│         │  - Claude Haiku (LLM)        │
│  - Categories       │         │  - Claude Sonnet (VLM)       │
│  - News events      │         │  - Titan Embeddings          │
│  - Scam tactics     │         └──────────────────────────────┘
└─────────────────────┘
      ▲
      │
┌─────┴───────────────────────────────────────────────────────┐
│                  Scam Pipeline (Batch Process)               │
│  1. RSS Crawler: Fetch news from multiple sources            │
│  2. Event Filter: Keyword matching & risk scoring            │
│  3. Tactic Extractor: LLM analysis of high-risk articles     │
│  4. Index Builder: Organize by keyword categories            │
│  5. Conclusion Agent: Generate risk report                   │
└─────────────────────────────────────────────────────────────┘
      ▲
      │
┌─────┴───────────────────────────────────────────────────────┐
│                  Classifier (Training Pipeline)              │
│  - Neural network training on labeled datasets               │
│  - Focal loss for imbalanced data                            │
│  - Calibration metrics (ECE, MCE, AECE)                      │
│  - Model checkpointing                                       │
└─────────────────────────────────────────────────────────────┘
      ▲
      │
┌─────┴───────────────────────────────────────────────────────┐
│                  Database (SQLite)                           │
│  - news_events: Crawled articles                             │
│  - event_analysis: LLM-extracted tactics                     │
│  - generated_cases: Training data                            │
│  - user_feedback: User interactions                          │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

#### User Query Flow (Real-time)

1. **User submits text or screenshot** via frontend
2. **Frontend** sends POST request to API server
3. **API Server** processes input:
   - If screenshot: VLM extracts text, URLs, phone numbers
   - Match text against keyword index
   - Call external APIs for URL/phone verification (optional)
4. **Conclusion Agent** synthesizes all data and makes final judgment
5. **API Server** returns structured result with:
   - is_scam (true/false/uncertain)
   - confidence score
   - scam_type
   - reasoning
   - red_flags
   - advice
6. **Frontend** displays results to user

#### Pipeline Flow (Batch)

1. **RSS Crawler** fetches articles from configured news sources
2. **Event Filter** scores articles by keyword matching:
   - 6 keyword categories with weighted scoring
   - Articles with score >= 3 are candidates
   - Articles with score >= 5 are high-risk
3. **Tactic Extractor** sends high-risk articles to LLM:
   - Extracts scam_tactics (list of methods)
   - Extracts impersonation_targets
   - Assigns risk_level (high/medium/low)
4. **Index Builder** organizes results by keyword category:
   - Creates keyword_index.json
   - Maps categories to relevant news + tactics
5. **Conclusion Agent** generates comprehensive risk report

## Components and Interfaces

### 1. Frontend (React + TypeScript)

**Technology Stack:**
- React 18 with TypeScript
- Vite for build tooling
- React Router for navigation
- Framer Motion for animations
- Material Design 3 color system

**Key Components:**

```typescript
// Main application component
App.tsx
  - Router configuration
  - Navigation (BottomNav, Header)
  - Screen routing

// Analysis screen
MessagesScreen
  - Text input area
  - Screenshot upload
  - Analysis trigger
  - Result display

// Result display
AnalysisResultPanel
  - Risk indicator
  - Scam type badge
  - Confidence score
  - Reasoning explanation
  - Red flags list
  - User advice

// API service
services/api.ts
  - analyzeText(text: string): Promise<AnalysisResult>
  - analyzeScreenshot(base64: string, text?: string): Promise<AnalysisResult>
```

**Interface: AnalysisResult**

```typescript
interface AnalysisResult {
  is_scam: boolean | "uncertain";
  confidence: number;  // 0.0 to 1.0
  scam_type: string | null;
  reasoning: string;
  red_flags: string[];
  advice: string;
  matched_news_event?: string;
  matched_tactic?: string;
}
```

### 2. API Server (Flask)

**Technology Stack:**
- Flask 3.x
- Flask-CORS for cross-origin requests
- Python 3.10+

**Endpoints:**

```python
POST /keyword-check
  Input:  {"text": string}
  Output: {
    "matched_categories": {category: [keywords]},
    "matched_context": {category: [articles]},
    "match_score": int,
    "has_match": bool
  }

POST /conclude
  Input: {
    "user_input": string,
    "keyword_match": object,
    "url_results": array,
    "number_results": array
  }
  Output: {
    "is_scam": bool | "uncertain",
    "confidence": float,
    "scam_type": string,
    "reasoning": string,
    "red_flags": array,
    "advice": string
  }

POST /vlm-analyze
  Input:  {"image_base64": string}
  Output: {
    "extracted_text": string,
    "urls": array,
    "phones": array,
    "image_type": string,
    "sender": string,
    "summary": string
  }

GET /health
  Output: {
    "status": "ok",
    "keyword_index_categories": int
  }
```

**Key Modules:**

```python
# api_server.py
- Flask app initialization
- CORS configuration
- Endpoint handlers
- Keyword index caching

# keyword_check.py
- load_keyword_index(): Load from JSON
- match_user_input(text, index): Match against patterns
- format_context_for_conclusion(): Prepare data for LLM

# conclusion_agent.py
- judge_user_input(context): Final scam judgment
- run_conclusion(keyword_index): Generate risk report
- _call_llm(prompt): Bedrock API wrapper
- _parse_json(text): Robust JSON parsing

# vlm_analyzer.py
- analyze_screenshot(bytes, format): Extract from image
- analyze_screenshot_base64(b64): Base64 wrapper
- _detect_format(b64): Auto-detect image type
```

### 3. Scam Pipeline (Batch Processing)

**Key Modules:**

```python
# pipeline.py
- run_pipeline(): Full end-to-end execution
- run_demo(): Test with hardcoded data
- build_keyword_index(articles): Organize by category

# crawler.py
- fetch_all_sources(max_per_source): Multi-source RSS fetch
- fetch_article_text(url): Full article scraping
- _clean_text(text): HTML removal and normalization

# event_filter.py
- filter_articles(articles): Keyword scoring
- _score_article(article): Calculate risk score
- _match_keywords(text): Find matching keywords

# analyzer.py
- extract_tactics(title, text): LLM tactic extraction
- _call_bedrock(prompt): Bedrock Converse API

# config.py
- SCAM_KEYWORDS: 6 categories with weights
- NEWS_SOURCES: RSS feed configurations
- TACTICS_PROMPT: LLM prompt template
- CONCLUSION_PROMPT: Final report template
```

**Keyword Categories:**

```python
SCAM_KEYWORDS = {
  "time_pressure": {weight: 2, words: ["截止", "限時", "延長", ...]},
  "official_event": {weight: 2, words: ["報稅", "補助", "國稅局", ...]},
  "money_flow": {weight: 2, words: ["匯款", "轉帳", "退款", ...]},
  "account_verify": {weight: 2, words: ["登入", "驗證", "密碼", ...]},
  "hot_events": {weight: 1, words: ["地震", "颱風", "疫情", ...]},
  "delivery_channel": {weight: 1, words: ["簡訊", "email", "連結", ...]}
}
```

### 4. Classifier (Neural Network)

**Architecture:**

```python
class EmbClassifier(nn.Module):
    def __init__(self, input_dim=1024, hidden_dim=256, n_class=2):
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, n_class)
        )
```

**Training Configuration:**

```python
# train.py
- Optimizer: AdamW
- Loss: FocalLoss / FocalLossAdaptive / CrossEntropyLoss
- Batch size: 32 (default)
- Learning rate: 1e-3 (default)
- Epochs: 10 (default)
- Random seed: 42 (for reproducibility)
```

**Focal Loss Implementation:**

```python
class FocalLoss(nn.Module):
    """
    Focal Loss = -α(1-pt)^γ * log(pt)
    Down-weights easy examples to focus on hard negatives
    """
    def __init__(self, gamma=2.0):
        self.gamma = gamma

class FocalLossAdaptive(nn.Module):
    """
    Adaptive Focal Loss with dynamic gamma adjustment
    Tracks per-sample difficulty across epochs
    """
    def __init__(self, gamma=2.0, device='cuda'):
        self.gamma = gamma
        self.difficulty_tracker = {}
```

**Calibration Metrics:**

```python
# metrics/metrics.py
- expected_calibration_error(confs, preds, labels, num_bins=15)
- maximum_calibration_error(confs, preds, labels, num_bins=15)
- adaptive_expected_calibration_error(confs, preds, labels, num_bins=15)
- test_classification_net(model, loader, device)
```

### 5. Embedder (Text and Image Embeddings)

**Models:**
- Text: Amazon Titan Text Embeddings V2
- Image: Amazon Titan Multimodal Embeddings G1
- Dimensions: 1024 (configurable)
- Normalization: Enabled by default

**Interface:**

```python
# embedder.py
def embed_text(text: str, dimensions: int = 1024) -> list[float]
def embed_image(image_path: str, dimensions: int = 1024) -> list[float]
def embed_text_and_image(text: str, image_path: str, dimensions: int = 1024) -> list[float]
def cosine_similarity(a: list[float], b: list[float]) -> float
```

### 6. VLM Analyzer (Screenshot Processing)

**Model:** Claude Sonnet 4.6 (Vision-Language Model)

**Extraction Capabilities:**
- Text content (main message area, excluding UI chrome)
- URLs (all visible links)
- Phone numbers (with country codes)
- Image type classification (sms/email/website/chat/notification/ad/other)
- Sender identification
- Objective summary

**System Prompt:**
```
你是一個圖片文字提取工具。你的任務是客觀地讀取圖片內容，不做任何主觀判斷。
請仔細觀察這張圖片，提取以下資訊：
1. extracted_text: 圖片主要區域中可見的文字內容
2. urls: 圖片中出現的所有網址
3. phones: 圖片中出現的所有電話號碼
4. image_type: 圖片類型
5. sender: 訊息的發送者或來源
6. summary: 一句話客觀描述這張圖片呈現的內容
```

## Data Models

### Database Schema (SQLite)

```sql
-- News articles from RSS feeds
CREATE TABLE news_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    source TEXT,
    url TEXT UNIQUE,
    published_at TEXT,
    raw_text TEXT,
    summary TEXT,
    keyword_score INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- LLM-extracted scam tactics
CREATE TABLE event_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    news_id INTEGER NOT NULL,
    scam_potential TEXT,
    reason TEXT,
    impersonation_targets TEXT,  -- JSON array
    likely_channels TEXT,         -- JSON array
    likely_actions TEXT,          -- JSON array
    scam_angles TEXT,             -- JSON array
    seasonality TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(news_id) REFERENCES news_events(id)
);

-- Generated training cases
CREATE TABLE generated_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    news_id INTEGER NOT NULL,
    title TEXT,
    event_hook TEXT,
    impersonated_entity TEXT,
    scam_goal TEXT,
    likely_channel TEXT,
    red_flags TEXT,              -- JSON array
    safe_response TEXT,
    embedding_id TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(news_id) REFERENCES news_events(id)
);

-- User feedback for model improvement
CREATE TABLE user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER,
    user_input TEXT,
    feedback_label TEXT,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(case_id) REFERENCES generated_cases(id)
);
```

### Keyword Index Structure (JSON)

```json
{
  "time_pressure": [
    {
      "title": "報稅截止日延長至6月底",
      "scam_tactics": [
        "假冒國稅局發送釣魚簡訊要求點擊連結",
        "聲稱逾期未報稅需立即繳納罰款"
      ],
      "impersonation_targets": ["國稅局", "財政部"],
      "risk_level": "high"
    }
  ],
  "official_event": [...],
  "money_flow": [...],
  "account_verify": [...],
  "hot_events": [...],
  "delivery_channel": [...]
}
```

### Configuration (config.py)

```python
# Bedrock Model IDs
LLM_MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
VLM_MODEL_ID = "us.anthropic.claude-sonnet-4-6"
EMBED_TEXT_MODEL_ID = "amazon.titan-embed-text-v2:0"
EMBED_MULTIMODAL_MODEL_ID = "amazon.titan-embed-image-v1"
BEDROCK_REGION = "us-west-2"

# Embedding configuration
EMBEDDING_DIMENSIONS = 1024

# Risk thresholds
SCORE_THRESHOLD_LOW = 2      # Discard
SCORE_THRESHOLD_MEDIUM = 4   # LLM analysis
# >= 5: High risk, direct to case generation

# News sources
NEWS_SOURCES = {
  "ltn": {"name": "自由時報", "rss": "...", "type": "rss"},
  "ettoday": {"name": "ETtoday", "rss": "...", "type": "rss"},
  "yahoo_tw": {"name": "Yahoo新聞", "rss": "...", "type": "rss"},
  "setn": {"name": "三立新聞", "rss": "...", "type": "rss", "needs_scrape_title": True}
}

# Database
DB_PATH = "scam_pipeline.db"
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: API Endpoint Text Acceptance

*For any* valid text input submitted to the /keyword-check endpoint, the API server should accept the request and return a structured JSON response containing matched_categories, matched_context, match_score, and has_match fields.

**Validates: Requirements 1.1**

### Property 2: Classifier Binary Output

*For any* 1024-dimensional embedding vector input to the classifier, the output should be a binary classification (class 0 or class 1) representing legitimate or scam.

**Validates: Requirements 1.2**

### Property 3: Confidence Score Range

*For any* prediction made by the classifier or conclusion agent, the confidence score should be a float value between 0.0 and 1.0 inclusive.

**Validates: Requirements 1.3, 10.4**

### Property 4: Keyword Matching Completeness

*For any* user input text containing keywords from the keyword index, the keyword matching algorithm should identify and return all matching categories and their associated keywords.

**Validates: Requirements 1.4, 9.1**

### Property 5: Conclusion Agent Data Integration

*For any* set of inputs (user_input, keyword_match, url_results, number_results) provided to the conclusion agent, the final judgment should reference and incorporate information from all provided data sources in its reasoning.

**Validates: Requirements 1.5, 10.1, 10.9**

#
ields.

**Validates: Requirements 2.1, 2.7**

### Property 8: VLM URL Extraction Completeness

*For any* screenshot image containing visible URLs, the VLM analyzer should extract and return all URLs present in the image.

**Validates: Requirements 2.3**

### Property 9: VLM Phone Number Extraction

*For any* screenshot image containing visible phone numbers, the VLM analyzer should extract and return all phone numbers with their country codes.

**Validates: Requirements 2.4**

### Property 10: VLM Image Type Classification

*For any* screenshot image analyzed by the VLM, the returned image_type should be one of the valid types: "sms", "email", "website", "chat", "notification", "ad", or "other".

**Validates: Requirements 2.5**

### Property 11: Text-Image Pipeline Consistency

*For any* text content, whether submitted directly as text or extracted from a screenshot, the analysis pipeline should produce equivalent results when the text content is identical.

**Validates: Requirements 2.8**

### Property 12: Classifier Input Dimension Validation

*For any* embedding vector with dimensions other than 1024, the classifier should reject the input or handle it appropriately without producing invalid predictions.

**Validates: Requirements 3.2**

### Property 13: Training Reproducibility

*For any* training run with the same random seed, dataset, and hyperparameters, the classifier should produce identical or near-identical model weights and training metrics.

**Validates: Requirements 3.10**

### Property 14: Focal Loss Formula Correctness

*For any* batch of predictions and labels, the focal loss calculation should match the formula: FL = -α(1-pt)^γ * log(pt), where pt is the predicted probability of the true class.

**Validates: Requirements 4.1**

### Property 15: Focal Loss Easy Example Down-weighting

*For any* pair of examples where one has higher prediction confidence (easier) and one has lower confidence (harder), the focal loss should assign lower loss to the easier example.

**Validates: Requirements 4.3**

### Property 16: Focal Loss Gamma Effect

*For any* set of predictions, increasing the gamma parameter should increase the relative down-weighting of easy examples compared to hard examples.

**Validates: Requirements 4.5**

### Property 17: RSS Crawler Article Extraction

*For any* configured RSS feed that is accessible, the crawler should successfully fetch articles and extract title, URL, publication date, summary, and source for each article.

**Validates: Requirements 5.1, 5.2**

### Property 18: Text Cleaning HTML Removal

*For any* extracted text containing HTML tags, the cleaning function should remove all HTML tags and normalize whitespace, returning plain text.

**Validates: Requirements 5.4**

### Property 19: Crawler Article Limit Enforcement

*For any* configured maximum articles per source, the crawler should fetch at most that number of articles from each source.

**Validates: Requirements 5.5**

### Property 20: Keyword Score Calculation

*For any* article text and set of matched keywords, the calculated score should equal the sum of weights for all matched keyword categories.

**Validates: Requirements 6.2**

### Property 21: Risk Level Threshold Classification

*For any* article with keyword score >= 3, the pipeline should mark it as a candidate for analysis; for score >= 5, it should mark it as high risk.

**Validates: Requirements 6.3, 6.4**

### Property 22: Keyword Match Tracking

*For any* article that matches keywords, the system should record which specific keywords matched and group them by category.

**Validates: Requirements 6.5, 6.6**

### Property 23: LLM Response Structure Validation

*For any* LLM response from tactic extraction, the parsed result should contain scam_tactics as a list, impersonation_targets as a list, and risk_level as one of "low", "medium", "high", or "unknown".

**Validates: Requirements 7.3, 7.4, 7.5**

### Property 24: LLM Input Text Truncation

*For any* article text sent to the LLM for analysis, the text should be truncated to at most 3000 characters before transmission.

**Validates: Requirements 7.7**

### Property 25: JSON Parsing Error Handling

*For any* invalid JSON response from an LLM, the parsing function should return a safe default structure containing an error field rather than raising an exception.

**Validates: Requirements 7.6, 20.2**

### Property 26: Keyword Index Structure

*For any* built keyword index, the structure should be a dictionary mapping category names (strings) to lists of article entries, where each entry contains title, scam_tactics, impersonation_targets, and risk_level.

**Validates: Requirements 8.1, 8.2**

### Property 27: Keyword Index Category Grouping

*For any* article that matches multiple keyword categories, the article entry should appear in the keyword index under all matched categories.

**Validates: Requirements 8.3**

### Property 28: Conclusion Agent Output Structure

*For any* input to the conclusion agent, the output should be a dictionary containing is_scam (bool or "uncertain"), confidence (float), scam_type (string or null), reasoning (string), red_flags (list), and advice (string).

**Validates: Requirements 10.3, 10.5, 10.6, 10.7, 10.8**

### Property 29: Embedding Normalization

*For any* text or image embedding generated with normalization enabled, the L2 norm of the embedding vector should be approximately 1.0 (within floating-point precision).

**Validates: Requirements 11.4**

### Property 30: Cosine Similarity Range

*For any* two embedding vectors, the cosine similarity should be a value between -1.0 and 1.0 inclusive.

**Validates: Requirements 11.6**

### Property 31: Base64 Image Handling

*For any* valid base64-encoded image string, the embedder should successfully decode and process the image to generate an embedding vector.

**Validates: Requirements 11.7**

### Property 32: Database Query Date Range

*For any* valid date range query on the analysis history, the database should return only records with timestamps falling within the specified range.

**Validates: Requirements 18.4**

### Property 33: API Error Response Structure

*For any* API request that encounters an error (LLM failure, missing data, etc.), the response should be a structured JSON object containing an error field with a descriptive message and an appropriate HTTP status code.

**Validates: Requirements 20.1**

### Property 34: Crawler Source Failure Resilience

*For any* set of news sources where one or more sources are unavailable, the crawler should continue processing the remaining available sources without terminating.

**Validates: Requirements 20.3, 20.4**

## Error Handling

### API Server Error Handling

1. **Missing Required Fields**: Return 400 Bad Request with error message
2. **LLM API Failures**: Return 502 Bad Gateway with error details
3. **JSON Parsing Failures**: Return safe default structure with error field
4. **Missing Keyword Index**: Health endpoint returns error status

### Pipeline Error Handling

1. **RSS Feed Unavailable**: Log error, continue with other sources
2. **Article Fetch Failure**: Log error, skip to next article
3. **LLM Call Failure**: Log error, use default values for that article
4. **JSON Parsing Error**: Return safe default structure

### Classifier Error Handling

1. **Invalid Input Dimensions**: Raise ValueError with clear message
2. **GPU Unavailable**: Fall back to CPU automatically
3. **Checkpoint Load Failure**: Raise FileNotFoundError with path

### Frontend Error Handling

1. **API Request Failure**: Display user-friendly error message
2. **Network Timeout**: Show retry button
3. **Invalid Input**: Disable analyze button, show validation message
4. **Image Upload Error**: Clear preview, show error toast

### Database Error Handling

1. **Connection Failure**: Retry with exponential backoff
2. **Constraint Violation**: Log and skip duplicate entries
3. **Query Failure**: Rollback transaction, return empty result

## Testing Strategy

### Dual Testing Approach

The system employs both unit testing and property-based testing for comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs
- Together: Unit tests catch concrete bugs, property tests verify general correctness

### Unit Testing

**Classifier Tests:**
- Test model initialization with various hidden dimensions
- Test forward pass with sample embeddings
- Test checkpoint saving and loading
- Test focal loss calculation with known inputs
- Test calibration metric computation

**API Tests:**
- Test each endpoint with valid inputs
- Test error responses for missing fields
- Test CORS headers
- Test health endpoint
- Test keyword index loading

**Pipeline Tests:**
- Test RSS parsing with sample feeds
- Test keyword matching with known articles
- Test score calculation
- Test index building
- Test demo mode execution

**Database Tests:**
- Test CRUD operations for each table
- Test foreign key constraints
- Test date range queries
- Test duplicate handling

### Property-Based Testing

**Testing Library:** Use `hypothesis` for Python, `fast-check` for TypeScript

**Configuration:** Minimum 100 iterations per property test

**Test Tagging:** Each property test must reference its design document property:
```python
# Feature: scam-detection-system, Property 3: Confidence Score Range
def test_confidence_score_range(confidence):
    assert 0.0 <= confidence <= 1.0
```

**Property Test Categories:**

1. **API Contract Properties:**
   - Response structure validation
   - Field type checking
   - Range constraints

2. **Data Processing Properties:**
   - Text cleaning idempotence
   - Keyword matching completeness
   - Score calculation correctness

3. **Model Properties:**
   - Input dimension validation
   - Output range constraints
   - Loss function monotonicity

4. **Integration Properties:**
   - Pipeline consistency
   - Error handling robustness
   - Data flow integrity

### Integration Testing

1. **End-to-End API Flow:**
   - Submit text → keyword check → conclusion → verify response
   - Submit screenshot → VLM analysis → keyword check → conclusion
   - Test with various scam and legitimate examples

2. **Pipeline Integration:**
   - Run full pipeline in demo mode
   - Verify keyword_index.json structure
   - Verify conclusion.json generation

3. **External API Integration:**
   - Test Bedrock API connectivity
   - Test error handling for API failures
   - Test rate limiting and retries

### Performance Testing

1. **API Response Time:**
   - /keyword-check: < 500ms
   - /conclude: < 2s (depends on LLM)
   - /vlm-analyze: < 3s (depends on VLM)

2. **Classifier Inference:**
   - Single prediction: < 10ms (GPU)
   - Batch prediction (32): < 50ms (GPU)

3. **Pipeline Throughput:**
   - Process 100 articles: < 5 minutes
   - Build keyword index: < 1 minute

### Test Data

1. **Labeled Datasets:**
   - spam_zh_tensor_splits/: Chinese spam detection
   - embedding_tensor_splits/: General scam detection
   - Split into train/val/test sets

2. **Synthetic Test Cases:**
   - Generate scam messages with known patterns
   - Generate legitimate messages
   - Generate edge cases (empty, very long, special characters)

3. **Real-World Examples:**
   - Collect actual scam messages (anonymized)
   - Collect legitimate messages
   - Maintain test suite with diverse examples

## Deployment Considerations

### Environment Variables

```bash
# Required
API_KEY=<bedrock-api-key>

# Optional
BEDROCK_REGION=us-west-2
DB_PATH=scam_pipeline.db
API_PORT=5001
API_HOST=0.0.0.0
```

### Dependencies

**Python (requirements.txt):**
```
flask>=3.0.0
flask-cors>=4.0.0
boto3>=1.34.0
python-dotenv>=1.0.0
torch>=2.0.0
feedparser>=6.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0
```

**Node.js (package.json):**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "framer-motion": "^10.16.0",
    "lucide-react": "^0.294.0"
  }
}
```

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Production Setup                      │
├─────────────────────────────────────────────────────────┤
│  Frontend (Vite build)                                   │
│    - Static files served by Nginx/CDN                    │
│    - Environment-specific API URLs                       │
├─────────────────────────────────────────────────────────┤
│  API Server (Flask)                                      │
│    - Gunicorn WSGI server                                │
│    - Multiple worker processes                           │
│    - Reverse proxy (Nginx)                               │
├─────────────────────────────────────────────────────────┤
│  Scam Pipeline (Cron job)                                │
│    - Scheduled execution (e.g., every 6 hours)           │
│    - Generates keyword_index.json                        │
│    - Updates database                                    │
├─────────────────────────────────────────────────────────┤
│  Database (SQLite)                                       │
│    - WAL mode for concurrent reads                       │
│    - Regular backups                                     │
├─────────────────────────────────────────────────────────┤
│  Classifier (Optional)                                   │
│    - Pre-trained model loaded at API startup             │
│    - GPU instance for inference                          │
└─────────────────────────────────────────────────────────┘
```

### Monitoring and Logging

1. **API Metrics:**
   - Request count by endpoint
   - Response time percentiles
   - Error rate
   - LLM API call success rate

2. **Pipeline Metrics:**
   - Articles processed per run
   - High-risk articles identified
   - LLM analysis success rate
   - Keyword index size

3. **Classifier Metrics:**
   - Inference latency
   - Prediction distribution
   - Confidence score distribution

4. **Logging:**
   - Structured JSON logs
   - Log levels: DEBUG, INFO, WARNING, ERROR
   - Sensitive data redaction (user inputs, API keys)

### Security Considerations

1. **API Security:**
   - HTTPS in production
   - Rate limiting per IP
   - Input validation and sanitization
   - CORS configuration

2. **Data Privacy:**
   - No logging of user message content
   - Anonymize any stored data
   - Clear data retention policy

3. **API Key Management:**
   - Environment variables only
   - No hardcoded keys
   - Rotate keys regularly
   - Use IAM roles in AWS

4. **Database Security:**
   - File permissions (600)
   - Regular backups
   - Encryption at rest (optional)

### Scalability Considerations

1. **API Server:**
   - Horizontal scaling with load balancer
   - Stateless design (keyword index in shared storage)
   - Connection pooling for database

2. **Pipeline:**
   - Parallel processing of news sources
   - Batch LLM requests where possible
   - Incremental updates to keyword index

3. **Classifier:**
   - Model serving with TorchServe or similar
   - Batch inference for multiple requests
   - Model quantization for faster inference

4. **Database:**
   - Consider PostgreSQL for high concurrency
   - Read replicas for analytics
   - Partitioning for large tables

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Frontend | React | 18.x | User interface |
| Frontend Build | Vite | 5.x | Build tooling |
| Frontend Routing | React Router | 6.x | Navigation |
| Frontend Animation | Framer Motion | 10.x | UI animations |
| API Server | Flask | 3.x | REST API |
| API CORS | Flask-CORS | 4.x | Cross-origin requests |
| LLM | Claude Haiku 4.5 | - | Reasoning and analysis |
| VLM | Claude Sonnet 4.6 | - | Screenshot analysis |
| Embeddings | Titan V2 / Multimodal G1 | - | Vector embeddings |
| ML Framework | PyTorch | 2.x | Neural network training |
| Database | SQLite | 3.x | Local data storage |
| RSS Parsing | feedparser | 6.x | News feed parsing |
| HTML Parsing | BeautifulSoup4 | 4.x | Web scraping |
| HTTP Client | requests | 2.x | API calls |
| AWS SDK | boto3 | 1.34+ | Bedrock integration |
| Environment | python-dotenv | 1.x | Configuration |

## Machine Learning Model Architecture

### Classifier Network

**Input Layer:**
- Dimension: 1024 (embedding vector)
- Type: Dense/Linear

**Hidden Layer 1:**
- Dimension: 256 (configurable)
- Normalization: Batch Normalization
- Activation: ReLU

**Hidden Layer 2:**
- Dimension: 256 (configurable)
- Normalization: Batch Normalization
- Activation: ReLU

**Output Layer:**
- Dimension: 2 (binary classification)
- Activation: None (logits)
- Post-processing: Softmax for probabilities

### Training Pipeline

```
1. Data Loading
   ├─ Load train.pt (embeddings + labels)
   ├─ Load val.pt (embeddings + labels)
   └─ Create DataLoaders (batch_size=32)

2. Model Initialization
   ├─ EmbClassifier(input_dim=1024, hidden_dim=256)
   ├─ Move to GPU if available
   └─ Set random seed for reproducibility

3. Loss Function Selection
   ├─ If --no_focal: CrossEntropyLoss
   ├─ If --adaptive: FocalLossAdaptive(gamma=2.0)
   └─ Else: FocalLoss(gamma=2.0)

4. Optimizer
   └─ AdamW(lr=1e-3)

5. Training Loop (10 epochs)
   ├─ Forward pass
   ├─ Loss calculation
   ├─ Backward pass
   ├─ Optimizer step
   ├─ Validation (every 2 epochs)
   ├─ Calibration metrics (every 1 epoch)
   └─ Checkpoint saving (every 2 epochs)

6. Final Model
   └─ Save model_final.pt
```

### Calibration Metrics

**Expected Calibration Error (ECE):**
- Measures average difference between confidence and accuracy
- Bins predictions by confidence level
- Lower is better (0 = perfect calibration)

**Maximum Calibration Error (MCE):**
- Measures worst-case calibration error across bins
- Identifies bins with largest miscalibration
- Lower is better

**Adaptive Expected Calibration Error (AECE):**
- Adjusts bin sizes based on prediction distribution
- More robust to imbalanced confidence distributions
- Lower is better

### Focal Loss Details

**Standard Focal Loss:**
```python
FL(pt) = -α(1 - pt)^γ * log(pt)

where:
  pt = predicted probability of true class
  α = class weight (optional)
  γ = focusing parameter (default 2.0)
```

**Adaptive Focal Loss:**
- Tracks per-sample difficulty across epochs
- Adjusts γ dynamically based on historical performance
- Focuses more on consistently difficult examples
- Reduces focus on examples that become easy

**Benefits:**
- Handles class imbalance effectively
- Focuses training on hard examples
- Reduces overfitting on easy examples
- Improves model robustness

## Conclusion

The Scam Detection System is a comprehensive, multi-layered platform that combines classical ML, modern LLMs, and real-time intelligence gathering to protect users from scams. The architecture is designed for modularity, allowing each component to be developed, tested, and deployed independently. The system prioritizes explainability, providing users with clear reasoning and actionable advice rather than just binary classifications.

Key strengths:
- **Multi-modal analysis**: Text, screenshots, URLs, phone numbers
- **Current intelligence**: Real-time news monitoring keeps detection up-to-date
- **Explainable AI**: Clear reasoning and red flags help users understand risks
- **Robust error handling**: Graceful degradation when services fail
- **Comprehensive testing**: Property-based and unit tests ensure correctness

Future enhancements:
- Real-time classifier integration for embedding-based detection
- User feedback loop for continuous model improvement
- Expanded news sources and languages
- Mobile app for on-device analysis
- Community-driven blacklist contributions
