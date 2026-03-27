# Requirements Document: Scam Detection System

## Introduction

The Scam Detection System (麥騙 FakeOff) is a comprehensive AI-driven platform for detecting and preventing phishing, scams, and malicious communications. The system combines multiple analysis techniques including machine learning classification, LLM-based reasoning, visual analysis, and real-time news monitoring to provide users with accurate scam detection and risk assessment.

The system serves end users through a web interface and API, enabling them to analyze suspicious messages, screenshots, URLs, and phone numbers. It also maintains a continuously updated knowledge base of scam tactics derived from news sources.

## Glossary

- **Scam_Detection_System**: The complete platform including all components (classifier, pipeline, API, frontend)
- **Classifier**: Neural network component that classifies text embeddings as scam or legitimate
- **Scam_Pipeline**: Backend service that crawls news, extracts scam tactics, and maintains keyword index
- **API_Server**: Flask-based REST API exposing detection services to clients
- **Frontend**: React-based web application for user interaction
- **VLM_Analyzer**: Visual Language Model component for analyzing screenshot images
- **Conclusion_Agent**: LLM-based reasoning component that makes final scam judgments
- **Keyword_Index**: Structured database mapping keyword categories to news events and scam tactics
- **Embedder**: Component that generates vector embeddings from text and images
- **LLM_Fingerprinting**: Forensic analysis tool for identifying which LLM generated a text
- **Focal_Loss**: Specialized loss function for training on imbalanced datasets
- **Adaptive_Gamma**: Dynamic parameter adjustment for focal loss during training
- **RSS_Crawler**: Component that fetches news articles from RSS feeds
- **Risk_Score**: Numerical assessment of scam likelihood based on keyword matching
- **Calibration_Metrics**: Measures of model confidence accuracy (ECE, MCE, AECE)

## Requirements

### Requirement 1: Text-Based Scam Classification

**User Story:** As a user, I want to submit suspicious text messages for analysis, so that I can determine if they are scams before taking action.

#### Acceptance Criteria

1. WHEN a user submits text input, THE API_Server SHALL accept the text via POST request to /keyword-check endpoint
2. THE Classifier SHALL process text embeddings and output a binary classification (scam or legitimate)
3. THE Classifier SHALL provide confidence scores between 0.0 and 1.0 for predictions
4. THE Keyword_Index SHALL match user input against known scam patterns from recent news
5. THE Conclusion_Agent SHALL synthesize classification results, keyword matches, and external API data into a final judgment
6. THE API_Server SHALL return structured JSON containing is_scam, confidence
nt from the image using Claude Sonnet VLM
3. THE VLM_Analyzer SHALL identify and extract all URLs present in the image
4. THE VLM_Analyzer SHALL identify and extract all phone numbers with country codes
5. THE VLM_Analyzer SHALL classify the image type (sms, email, website, chat, notification, ad, other)
6. THE VLM_Analyzer SHALL identify the sender or source of the message
7. THE VLM_Analyzer SHALL return extracted information as structured JSON
8. THE API_Server SHALL process extracted text through the same analysis pipeline as text input

### Requirement 3: Neural Network Classifier Training

**User Story:** As a system administrator, I want to train the classifier on labeled datasets, so that the model can accurately distinguish scams from legitimate messages.

#### Acceptance Criteria

1. THE Classifier SHALL use a three-layer neural network architecture with batch normalization
2. THE Classifier SHALL accept 1024-dimensional embedding vectors as input
3. WHERE focal loss is enabled, THE Classifier SHALL use FocalLoss or FocalLossAdaptive for training
4. WHERE focal loss is disabled, THE Classifier SHALL use standard CrossEntropyLoss
5. THE Classifier SHALL support configurable hidden layer dimensions
6. THE Classifier SHALL train on separate train and validation datasets loaded from .pt files
7. THE Classifier SHALL compute and log ECE, MCE, and Adaptive ECE calibration metrics during training
8. THE Classifier SHALL save model checkpoints at configurable intervals
9. THE Classifier SHALL use AdamW optimizer with configurable learning rate
10. THE Classifier SHALL set random seeds for reproducible training results

### Requirement 4: Focal Loss Implementation

**User Story:** As a machine learning engineer, I want to use focal loss for training, so that the model handles class imbalance effectively.

#### Acceptance Criteria

1. THE FocalLoss SHALL implement the focal loss formula with configurable gamma parameter
2. THE FocalLossAdaptive SHALL dynamically adjust gamma based on classification difficulty
3. THE FocalLoss SHALL down-weight easy examples to focus on hard negatives
4. THE FocalLossAdaptive SHALL track per-sample difficulty across training epochs
5. WHERE gamma is higher, THE FocalLoss SHALL apply stronger down-weighting to easy examples
6. THE Classifier SHALL support switching between standard focal loss and adaptive focal loss via command-line flag

### Requirement 5: News Crawling and Monitoring

**User Story:** As the system, I want to continuously monitor news sources for scam-related events, so that I can maintain an up-to-date knowledge base of current scam tactics.

#### Acceptance Criteria

1. THE RSS_Crawler SHALL fetch articles from configured RSS feeds (自由時報, ETtoday, Yahoo, 三立)
2. THE RSS_Crawler SHALL extract title, URL, publication date, summary, and source for each article
3. THE RSS_Crawler SHALL handle articles that require title scraping from HTML
4. THE RSS_Crawler SHALL clean extracted text by removing HTML tags and normalizing whitespace
5. THE RSS_Crawler SHALL support configurable maximum articles per source
6. THE RSS_Crawler SHALL set appropriate User-Agent headers to avoid blocking
7. WHERE an article URL is provided, THE RSS_Crawler SHALL optionally fetch full article text

### Requirement 6: Keyword-Based Risk Scoring

**User Story:** As the system, I want to score news articles by scam exploitation potential, so that I can prioritize high-risk events for analysis.

#### Acceptance Criteria

1. THE Scam_Pipeline SHALL maintain six keyword categories: time_pressure, official_event, financial, account_verification, high_profile_event, notification_link
2. THE Scam_Pipeline SHALL assign weighted scores to keyword matches (+2 for critical categories, +1 for moderate)
3. WHEN an article matches keywords with total score >= 3, THE Scam_Pipeline SHALL mark it as a candidate for LLM analysis
4. WHEN an article matches keywords with total score >= 5, THE Scam_Pipeline SHALL mark it as high risk
5. THE Scam_Pipeline SHALL track which specific keywords matched for each article
6. THE Scam_Pipeline SHALL group matched keywords by category for structured output

### Requirement 7: LLM-Based Tactic Extraction

**User Story:** As the system, I want to extract scam tactics from news articles using LLMs, so that I can build a knowledge base of current scam methods.

#### Acceptance Criteria

1. WHEN a high-risk article is identified, THE Scam_Pipeline SHALL send title and text to the LLM analyzer
2. THE Scam_Pipeline SHALL use Amazon Bedrock Claude Haiku for tactic extraction
3. THE Scam_Pipeline SHALL extract scam_tactics as a list of specific methods described in the article
4. THE Scam_Pipeline SHALL extract impersonation_targets as a list of entities being impersonated
5. THE Scam_Pipeline SHALL extract risk_level as a categorical assessment (high, medium, low, unknown)
6. THE Scam_Pipeline SHALL parse LLM responses as JSON and handle parsing errors gracefully
7. THE Scam_Pipeline SHALL truncate article text to 3000 characters before sending to LLM

### Requirement 8: Keyword Index Construction

**User Story:** As the system, I want to organize extracted scam tactics by keyword category, so that I can quickly match user queries to relevant scam patterns.

#### Acceptance Criteria

1. THE Scam_Pipeline SHALL build a Keyword_Index mapping categories to lists of article entries
2. FOR EACH analyzed article, THE Scam_Pipeline SHALL create an entry containing title, scam_tactics, impersonation_targets, and risk_level
3. THE Scam_Pipeline SHALL group entries by their matched keyword categories
4. THE Scam_Pipeline SHALL save the Keyword_Index as keyword_index.json
5. THE Keyword_Index SHALL use UTF-8 encoding with ensure_ascii=False for proper Chinese character handling
6. THE API_Server SHALL load the Keyword_Index at startup and cache it in memory

### Requirement 9: User Input Matching

**User Story:** As a user, I want my suspicious message matched against recent scam patterns, so that I can see if it resembles known scam tactics.

#### Acceptance Criteria

1. WHEN a user submits text, THE API_Server SHALL match it against all keyword categories in the Keyword_Index
2. THE API_Server SHALL return matched_categories as a dictionary mapping categories to matched keywords
3. THE API_Server SHALL return matched_context containing relevant news articles and their scam tactics
4. THE API_Server SHALL compute a match_score based on the number and weight of matched keywords
5. THE API_Server SHALL set has_match to true if any keywords match
6. THE API_Server SHALL format matched context for consumption by the Conclusion_Agent

### Requirement 10: Comprehensive Scam Judgment

**User Story:** As a user, I want a final AI-powered judgment on whether my message is a scam, so that I can make an informed decision.

#### Acceptance Criteria

1. THE Conclusion_Agent SHALL receive user input, keyword matches, URL results, and phone number results
2. THE Conclusion_Agent SHALL use Amazon Bedrock Claude Haiku for reasoning
3. THE Conclusion_Agent SHALL output is_scam as true, false, or "uncertain"
4. THE Conclusion_Agent SHALL output confidence as a float between 0.0 and 1.0
5. THE Conclusion_Agent SHALL identify scam_type (e.g., "假冒官方通知", "釣魚簡訊", "假客服電話")
6. THE Conclusion_Agent SHALL provide reasoning explaining the judgment in natural language
7. THE Conclusion_Agent SHALL list red_flags identifying suspicious features in the message
8. THE Conclusion_Agent SHALL provide advice in language understandable to general users
9. THE Conclusion_Agent SHALL cross-reference URL risk scores and phone spam indicators in its judgment
10. WHERE URL results show high risk scores or blacklisting, THE Conclusion_Agent SHALL weight this heavily in the judgment

### Requirement 11: Text Embedding Generation

**User Story:** As the system, I want to generate vector embeddings from text and images, so that I can perform similarity-based analysis and classification.

#### Acceptance Criteria

1. THE Embedder SHALL use Amazon Titan Text Embeddings V2 for text embedding
2. THE Embedder SHALL use Amazon Titan Multimodal Embeddings G1 for image embedding
3. THE Embedder SHALL support configurable embedding dimensions (default 1024)
4. THE Embedder SHALL normalize embeddings by default
5. THE Embedder SHALL support text-only, image-only, and combined text-image embedding modes
6. THE Embedder SHALL provide cosine_similarity function for comparing embeddings
7. THE Embedder SHALL handle base64-encoded images for multimodal embedding

### Requirement 12: LLM Fingerprinting for Data Alignment

**User Story:** As a data analyst, I want to identify which LLM generated scam messages, so that I can track AI-generated fraud campaigns.

#### Acceptance Criteria

1. THE LLM_Fingerprinting SHALL analyze messages against fingerprints of 6 candidate LLMs (GPT, Claude, Gemini, Llama, Mistral, Qwen)
2. THE LLM_Fingerprinting SHALL use three judge models (Claude Sonnet 4.5, GPT-4o, Llama 3-70B) for consensus scoring
3. THE LLM_Fingerprinting SHALL score each message on word choice, grammar, format, and tone markers
4. THE LLM_Fingerprinting SHALL aggregate scores across judges to identify the most likely source
5. THE LLM_Fingerprinting SHALL compute confidence gap between top match and second match
6. THE LLM_Fingerprinting SHALL flag low-confidence attributions for manual review
7. THE LLM_Fingerprinting SHALL process Excel datasets with automatic deduplication
8. THE LLM_Fingerprinting SHALL support resume-safe incremental CSV output
9. THE LLM_Fingerprinting SHALL generate summary reports with match frequencies and ambiguous messages

### Requirement 13: Translation Service

**User Story:** As a data analyst, I want to translate scam messages to Traditional Chinese, so that I can analyze messages from multiple language sources.

#### Acceptance Criteria

1. THE Translation_Service SHALL use Qwen3-30B-A3B-Instruct-2507 for translation
2. THE Translation_Service SHALL translate messages to Traditional Chinese
3. THE Translation_Service SHALL preserve technical terms and proper nouns during translation
4. THE Translation_Service SHALL maintain message structure and formatting

### Requirement 14: REST API Endpoints

**User Story:** As a client application, I want to access scam detection services via REST API, so that I can integrate detection into various platforms.

#### Acceptance Criteria

1. THE API_Server SHALL expose POST /keyword-check endpoint accepting {"text": "..."}
2. THE API_Server SHALL expose POST /conclude endpoint accepting user_input, keyword_match, url_results, and number_results
3. THE API_Server SHALL expose POST /vlm-analyze endpoint accepting {"image_base64": "..."}
4. THE API_Server SHALL expose GET /health endpoint returning service status
5. THE API_Server SHALL enable CORS for cross-origin requests
6. THE API_Server SHALL return JSON responses with appropriate HTTP status codes
7. THE API_Server SHALL handle missing required fields with 400 Bad Request
8. THE API_Server SHALL handle LLM call failures with 502 Bad Gateway
9. THE API_Server SHALL support configurable host and port via command-line arguments
10. THE API_Server SHALL load and cache the Keyword_Index at startup

### Requirement 15: Web Frontend Interface

**User Story:** As a user, I want a web interface to analyze suspicious messages, so that I can easily access scam detection without technical knowledge.

#### Acceptance Criteria

1. THE Frontend SHALL provide a text input area for pasting suspicious messages
2. THE Frontend SHALL provide a paste button for quick clipboard access
3. THE Frontend SHALL provide an upload button for screenshot analysis
4. THE Frontend SHALL display image previews with remove functionality
5. THE Frontend SHALL show loading indicators during analysis
6. THE Frontend SHALL display analysis results with visual risk indicators
7. THE Frontend SHALL show scam type, confidence, reasoning, red flags, and advice
8. THE Frontend SHALL provide navigation to News, Record, and Blacklist sections
9. THE Frontend SHALL display recent analysis history in a sidebar
10. THE Frontend SHALL use Material Design 3 color system for consistent theming
11. THE Frontend SHALL be responsive and mobile-friendly
12. THE Frontend SHALL disable the analyze button when no input is provided

### Requirement 16: Model Calibration Metrics

**User Story:** As a machine learning engineer, I want to measure model calibration, so that I can ensure confidence scores accurately reflect prediction accuracy.

#### Acceptance Criteria

1. THE Classifier SHALL compute Expected Calibration Error (ECE) during validation
2. THE Classifier SHALL compute Maximum Calibration Error (MCE) during validation
3. THE Classifier SHALL compute Adaptive Expected Calibration Error (AECE) during validation
4. THE Classifier SHALL support configurable number of bins for calibration (default 15)
5. THE Classifier SHALL log all three calibration metrics at configurable intervals
6. THE Classifier SHALL compute calibration metrics on the validation set, not training set

### Requirement 17: Pipeline Orchestration

**User Story:** As a system administrator, I want to run the complete pipeline end-to-end, so that I can update the knowledge base with current scam intelligence.

#### Acceptance Criteria

1. THE Scam_Pipeline SHALL support demo mode with hardcoded test data
2. THE Scam_Pipeline SHALL support full mode with live RSS crawling
3. THE Scam_Pipeline SHALL execute steps in order: crawl, filter, extract tactics, build index, generate conclusion
4. THE Scam_Pipeline SHALL save keyword_index.json and conclusion.json as output
5. THE Scam_Pipeline SHALL log progress for each step with article counts and risk levels
6. THE Scam_Pipeline SHALL handle LLM call failures gracefully without stopping the pipeline
7. THE Scam_Pipeline SHALL support configurable max articles per source

### Requirement 18: Database Schema for Analysis History

**User Story:** As the system, I want to store analysis history in a database, so that users can review past analyses and track patterns over time.

#### Acceptance Criteria

1. THE Scam_Detection_System SHALL use SQLite for local data storage
2. THE Scam_Detection_System SHALL define schema for storing user queries, analysis results, and timestamps
3. THE Scam_Detection_System SHALL provide CRUD operations for analysis records
4. THE Scam_Detection_System SHALL support querying analysis history by date range
5. THE Scam_Detection_System SHALL store extracted URLs and phone numbers separately for blacklist building

### Requirement 19: Configuration Management

**User Story:** As a system administrator, I want centralized configuration, so that I can easily adjust system parameters without code changes.

#### Acceptance Criteria

1. THE Scam_Detection_System SHALL load API keys from environment variables
2. THE Scam_Detection_System SHALL define model IDs in a central config module
3. THE Scam_Detection_System SHALL define keyword categories and weights in config
4. THE Scam_Detection_System SHALL define LLM prompt templates in config
5. THE Scam_Detection_System SHALL define news source RSS feeds in config
6. THE Scam_Detection_System SHALL support .env files for local development
7. THE Scam_Detection_System SHALL provide .env.example as a template

### Requirement 20: Error Handling and Resilience

**User Story:** As a user, I want the system to handle errors gracefully, so that temporary failures don't prevent me from getting results.

#### Acceptance Criteria

1. WHEN an LLM API call fails, THE Scam_Detection_System SHALL log the error and return a structured error response
2. WHEN JSON parsing fails, THE Scam_Detection_System SHALL return a default safe structure
3. WHEN a news source is unavailable, THE RSS_Crawler SHALL continue with other sources
4. WHEN an article cannot be fetched, THE RSS_Crawler SHALL log the error and skip to the next article
5. WHEN the Keyword_Index file is missing, THE API_Server SHALL return an error on /health endpoint
6. THE Frontend SHALL display user-friendly error messages for API failures
7. THE Frontend SHALL allow users to retry failed analyses

### Requirement 21: Performance and Scalability

**User Story:** As a system administrator, I want the system to handle multiple concurrent requests efficiently, so that users experience minimal latency.

#### Acceptance Criteria

1. THE API_Server SHALL cache the Keyword_Index in memory to avoid repeated file reads
2. THE API_Server SHALL support concurrent request handling via Flask
3. THE Classifier SHALL support GPU acceleration when available
4. THE Classifier SHALL fall back to CPU when GPU is unavailable
5. THE VLM_Analyzer SHALL process images without storing them to disk
6. THE Embedder SHALL batch process multiple texts when possible

### Requirement 22: Security and Privacy

**User Story:** As a user, I want my submitted messages to be handled securely, so that my private information is protected.

#### Acceptance Criteria

1. THE API_Server SHALL not log user-submitted message content
2. THE API_Server SHALL use HTTPS in production deployments
3. THE API_Server SHALL validate and sanitize all user inputs
4. THE Frontend SHALL not store user messages in browser local storage
5. THE Scam_Detection_System SHALL not share user data with third parties
6. THE Scam_Detection_System SHALL use API keys securely via environment variables, not hardcoded

### Requirement 23: Testing and Validation

**User Story:** As a developer, I want comprehensive test utilities, so that I can validate system functionality before deployment.

#### Acceptance Criteria

1. THE Scam_Detection_System SHALL provide test scripts for Bedrock API connectivity
2. THE Scam_Detection_System SHALL provide end-to-end API flow tests
3. THE Scam_Detection_System SHALL provide demo mode for testing without live data
4. THE Classifier SHALL provide test utilities for out-of-distribution detection
5. THE Classifier SHALL compute confusion matrix, accuracy, precision, recall, and F1 score on test sets
6. THE LLM_Fingerprinting SHALL support --limit flag for quick testing with subset of data

### Requirement 24: Deployment and Operations

**User Story:** As a system administrator, I want clear deployment instructions, so that I can set up the system in production environments.

#### Acceptance Criteria

1. THE Scam_Detection_System SHALL provide requirements.txt for Python dependencies
2. THE Scam_Detection_System SHALL provide package.json for Node.js dependencies
3. THE Scam_Detection_System SHALL document all required environment variables
4. THE Scam_Detection_System SHALL support Docker deployment for n8n workflow integration
5. THE Scam_Detection_System SHALL provide health check endpoints for monitoring
6. THE API_Server SHALL support configurable host and port for flexible deployment
7. THE Frontend SHALL support production builds via Vite

### Requirement 25: Documentation and Usability

**User Story:** As a new user or developer, I want comprehensive documentation, so that I can understand and use the system effectively.

#### Acceptance Criteria

1. THE Scam_Detection_System SHALL provide a main README with system architecture diagram
2. THE Scam_Detection_System SHALL document all API endpoints with request/response examples
3. THE Scam_Detection_System SHALL provide quick start guides for each component
4. THE Scam_Detection_System SHALL document the complete pipeline flow
5. THE Scam_Detection_System SHALL provide usage examples for command-line tools
6. THE Classifier SHALL document training arguments and their effects
7. THE LLM_Fingerprinting SHALL document how to add new candidate models and judges
