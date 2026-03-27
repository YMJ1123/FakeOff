# Implementation Plan: Scam Detection System

## Overview

The Scam Detection System (麥騙 FakeOff) is a comprehensive AI-driven platform combining neural network classification, LLM-based reasoning, visual analysis, and real-time news monitoring for scam detection. The implementation uses Python for backend services (Flask API, PyTorch classifier, news pipeline) and TypeScript/React for the frontend interface.

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Create directory structure for classifier, scam-pipeline, and frontend
  - Define Python requirements (Flask, PyTorch, boto3, feedparser, beautifulsoup4)
  - Define Node.js dependencies (React, Vite, React Router, Framer Motion)
  - Create environment configuration files (.env.example)
  - _Requirements: 19.1, 19.2, 19.6, 19.7, 24.1, 24.2_

- [ ] 2. Implement neural network classifier
  - [ ] 2.1 Create classifier model architecture
    - Implement EmbClassifier with three-layer neural network
    - Add batch normalization and ReLU activation layers
    - Support configurable input dimensions (1024) and hidden dimensions
    - _Requirements: 3.1, 3.2, 3.5_
  
  - [ ] 2.2 Implement focal loss functions
    - Create FocalLoss class with configurable gamma parameter
    - Create FocalLossAdaptive with dynamic gamma adjustment
    - Implement down-weighting logic for easy examples
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [ ]* 2.3 Write property test for focal loss
    - **Property 14: Focal Loss Formula Correctness**
    - **Property 15: Focal Loss Easy Example Down-weighting**
    - **Property 16: Focal Loss Gamma Effect**
    - **Validates: Requirements 4.1, 4.3, 4.5**
  
  - [ ] 2.4 Implement calibration metrics
    - Create expected_calibration_error function with configurable bins
    - Create maximum_calibration_error function
    - Create adaptive_expected_calibration_error function
    - Implement test_classification_net for evaluation
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6_
  
  - [ ]* 2.5 Write property test for calibration metrics
    - **Property 33: API Error Response Structure**
    - **Validates: Requirements 16.1, 16.2, 16.3**
  
  - [ ] 2.6 Create training pipeline
    - Implement data loading from .pt files
    - Create training loop with AdamW optimizer
    - Add validation and checkpoint saving logic
    - Implement random seed setting for reproducibility
    - Support command-line arguments for hyperparameters
    - _Requirements: 3.3, 3.4, 3.6, 3.7, 3.8, 3.9, 3.10_
  
  - [ ]* 2.7 Write property test for classifier
    - **Property 2: Classifier Binary Output**
    - **Property 12: Classifier Input Dimension Validation**
    - **Property 13: Training Reproducibility**
    - **Validates: Requirements 3.2, 3.10**

- [ ] 3. Checkpoint - Ensure classifier tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement embedding generation service
  - [ ] 4.1 Create embedder module
    - Implement embed_text using Amazon Titan Text Embeddings V2
    - Implement embed_image using Amazon Titan Multimodal Embeddings G1
    - Implement embed_text_and_image for combined embeddings
    - Add cosine_similarity function for vector comparison
    - Support configurable dimensions and normalization
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_
  
  - [ ]* 4.2 Write property test for embeddings
    - **Property 29: Embedding Normalization**
    - **Property 30: Cosine Similarity Range**
    - **Property 31: Base64 Image Handling**
    - **Validates: Requirements 11.4, 11
shot_base64 wrapper
    - Auto-detect image format from base64 data
    - Handle data URL prefixes
    - _Requirements: 2.1_
  
  - [ ]* 5.3 Write property test for VLM analyzer
    - **Property 7: VLM Response Structure**
    - **Property 8: VLM URL Extraction Completeness**
    - **Property 9: VLM Phone Number Extraction**
    - **Property 10: VLM Image Type Classification**
    - **Validates: Requirements 2.2, 2.3, 2.4, 2.5**

- [ ] 6. Implement news crawling and filtering
  - [ ] 6.1 Create RSS crawler
    - Implement fetch_all_sources for multi-source RSS fetching
    - Extract title, URL, publication date, summary, and source
    - Handle articles requiring title scraping from HTML
    - Clean extracted text by removing HTML tags
    - Support configurable max articles per source
    - Set appropriate User-Agent headers
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [ ] 6.2 Create event filter with keyword scoring
    - Define six keyword categories with weighted scores
    - Implement keyword matching against article text
    - Calculate risk scores based on matched keywords
    - Mark articles as candidates (score >= 3) or high-risk (score >= 5)
    - Track which specific keywords matched
    - Group matched keywords by category
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [ ]* 6.3 Write property test for keyword scoring
    - **Property 20: Keyword Score Calculation**
    - **Property 21: Risk Level Threshold Classification**
    - **Property 22: Keyword Match Tracking**
    - **Validates: Requirements 6.2, 6.3, 6.4, 6.5, 6.6**
  
  - [ ]* 6.4 Write property test for RSS crawler
    - **Property 17: RSS Crawler Article Extraction**
    - **Property 18: Text Cleaning HTML Removal**
    - **Property 19: Crawler Article Limit Enforcement**
    - **Property 34: Crawler Source Failure Resilience**
    - **Validates: Requirements 5.1, 5.2, 5.4, 5.5, 20.3, 20.4**

- [ ] 7. Checkpoint - Ensure crawler and filter tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement LLM-based analysis
  - [ ] 8.1 Create tactic extraction module
    - Implement extract_tactics using Amazon Bedrock Claude Haiku
    - Extract scam_tactics as list of methods
    - Extract impersonation_targets as list of entities
    - Extract risk_level (high/medium/low/unknown)
    - Parse LLM responses as JSON with error handling
    - Truncate article text to 3000 characters before LLM call
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_
  
  - [ ] 8.2 Create conclusion agent
    - Implement run_conclusion for news-only mode
    - Implement judge_user_input for user-query mode
    - Synthesize keyword matches, URL results, and phone results
    - Output is_scam (true/false/uncertain)
    - Output confidence score (0.0-1.0)
    - Identify scam_type
    - Provide reasoning and red_flags
    - Provide user-friendly advice
    - Cross-reference URL risk scores and phone spam indicators
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10_
  
  - [ ]* 8.3 Write property test for LLM responses
    - **Property 23: LLM Response Structure Validation**
    - **Property 24: LLM Input Text Truncation**
    - **Property 25: JSON Parsing Error Handling**
    - **Property 28: Conclusion Agent Output Structure**
    - **Validates: Requirements 7.3, 7.4, 7.5, 7.6, 7.7, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8**

- [ ] 9. Build keyword index and pipeline orchestration
  - [ ] 9.1 Create keyword index builder
    - Implement build_keyword_index to group articles by category
    - Create entries with title, scam_tactics, impersonation_targets, risk_level
    - Save keyword_index.json with UTF-8 encoding
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ] 9.2 Create keyword matching service
    - Implement load_keyword_index from JSON file
    - Implement match_user_input against keyword index
    - Return matched_categories with matched keywords
    - Return matched_context with relevant news articles
    - Compute match_score based on keyword weights
    - Set has_match flag
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_
  
  - [ ] 9.3 Create pipeline orchestrator
    - Implement run_pipeline for full end-to-end execution
    - Implement run_demo with hardcoded test data
    - Execute steps: crawl, filter, extract tactics, build index, generate conclusion
    - Save keyword_index.json and conclusion.json
    - Log progress for each step
    - Handle LLM call failures gracefully
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7_
  
  - [ ]* 9.4 Write property test for keyword index
    - **Property 26: Keyword Index Structure**
    - **Property 27: Keyword Index Category Grouping**
    - **Property 4: Keyword Matching Completeness**
    - **Validates: Requirements 8.1, 8.2, 8.3, 9.1**

- [ ] 10. Checkpoint - Ensure pipeline tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement REST API server
  - [ ] 11.1 Create Flask API server
    - Initialize Flask app with CORS support
    - Implement /keyword-check endpoint
    - Implement /conclude endpoint
    - Implement /vlm-analyze endpoint
    - Implement /health endpoint
    - Load and cache keyword index at startup
    - Support configurable host and port
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.9, 14.10_
  
  - [ ] 11.2 Add API error handling
    - Return 400 Bad Request for missing required fields
    - Return 502 Bad Gateway for LLM call failures
    - Return appropriate HTTP status codes
    - Handle JSON parsing errors gracefully
    - _Requirements: 14.7, 14.8, 20.1, 20.2_
  
  - [ ]* 11.3 Write property test for API endpoints
    - **Property 1: API Endpoint Text Acceptance**
    - **Property 3: Confidence Score Range**
    - **Property 5: Conclusion Agent Data Integration**
    - **Property 11: Text-Image Pipeline Consistency**
    - **Property 33: API Error Response Structure**
    - **Validates: Requirements 1.1, 1.3, 1.5, 2.8, 14.1, 14.2, 14.3, 14.7, 14.8, 20.1**
  
  - [ ]* 11.4 Write integration tests for API flow
    - Test end-to-end text analysis flow
    - Test end-to-end screenshot analysis flow
    - Test error handling for various failure scenarios
    - _Requirements: 23.2_

- [ ] 12. Implement web frontend interface
  - [ ] 12.1 Create React application structure
    - Set up Vite build configuration
    - Configure React Router for navigation
    - Implement Material Design 3 color system
    - Create responsive layout with mobile support
    - _Requirements: 15.11, 15.12, 24.7_
  
  - [ ] 12.2 Create main analysis screen
    - Implement text input area with paste functionality
    - Implement screenshot upload with preview
    - Add analyze button with loading state
    - Disable analyze button when no input provided
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.12_
  
  - [ ] 12.3 Create analysis result display
    - Display scam type with visual risk indicators
    - Show confidence score
    - Display reasoning explanation
    - List red flags
    - Provide user advice
    - _Requirements: 15.6, 15.7_
  
  - [ ] 12.4 Create navigation and additional screens
    - Implement bottom navigation bar
    - Create News screen placeholder
    - Create Record screen placeholder
    - Create Blacklist screen placeholder
    - Add recent analysis history sidebar
    - _Requirements: 15.8, 15.9_
  
  - [ ] 12.5 Implement API service layer
    - Create analyzeText function calling /keyword-check and /conclude
    - Create analyzeScreenshot function calling /vlm-analyze
    - Handle API errors with user-friendly messages
    - _Requirements: 15.6, 20.6_
  
  - [ ]* 12.6 Write integration tests for frontend
    - Test user input flow
    - Test screenshot upload flow
    - Test error display
    - Test navigation
    - _Requirements: 23.2_

- [ ] 13. Implement database schema and operations
  - [ ] 13.1 Create SQLite database schema
    - Define news_events table
    - Define event_analysis table
    - Define generated_cases table
    - Define user_feedback table
    - Set up foreign key constraints
    - _Requirements: 18.1, 18.2_
  
  - [ ] 13.2 Implement database operations
    - Create CRUD operations for analysis records
    - Implement date range queries
    - Store extracted URLs and phone numbers separately
    - _Requirements: 18.3, 18.4, 18.5_
  
  - [ ]* 13.3 Write property test for database operations
    - **Property 32: Database Query Date Range**
    - **Validates: Requirements 18.4**

- [ ] 14. Implement configuration management
  - [ ] 14.1 Create central configuration module
    - Define Bedrock model IDs
    - Define keyword categories and weights
    - Define LLM prompt templates
    - Define news source RSS feeds
    - Define risk thresholds
    - _Requirements: 19.2, 19.3, 19.4, 19.5_
  
  - [ ] 14.2 Set up environment variable loading
    - Load API keys from environment variables
    - Support .env files for local development
    - Provide .env.example template
    - _Requirements: 19.1, 19.6, 19.7, 22.6_

- [ ] 15. Implement LLM fingerprinting for data alignment
  - [ ] 15.1 Create LLM fingerprinting module
    - Implement analysis against 6 candidate LLMs
    - Use three judge models for consensus scoring
    - Score on word choice, grammar, format, and tone markers
    - Aggregate scores to identify most likely source
    - Compute confidence gap between top matches
    - Flag low-confidence attributions
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_
  
  - [ ] 15.2 Add dataset processing capabilities
    - Process Excel datasets with deduplication
    - Support resume-safe incremental CSV output
    - Generate summary reports with match frequencies
    - Support --limit flag for testing
    - _Requirements: 12.7, 12.8, 12.9, 23.6_
  
  - [ ]* 15.3 Write unit tests for fingerprinting
    - Test judge scoring logic
    - Test aggregation algorithm
    - Test confidence calculation
    - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [ ] 16. Implement translation service
  - [ ] 16.1 Create translation module
    - Use Qwen3-30B-A3B-Instruct-2507 for translation
    - Translate to Traditional Chinese
    - Preserve technical terms and proper nouns
    - Maintain message structure and formatting
    - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [ ] 17. Add testing utilities and validation
  - [ ] 17.1 Create API connectivity tests
    - Test Bedrock API connection
    - Test text embedding generation
    - Test VLM analysis
    - _Requirements: 23.1_
  
  - [ ] 17.2 Create classifier test utilities
    - Implement out-of-distribution detection tests
    - Compute confusion matrix, accuracy, precision, recall, F1
    - _Requirements: 23.4, 23.5_
  
  - [ ] 17.3 Create demo mode for testing
    - Implement demo mode with hardcoded data
    - Test pipeline without live data
    - _Requirements: 23.3_

- [ ] 18. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 19. Documentation and deployment preparation
  - [ ] 19.1 Create comprehensive documentation
    - Write main README with system architecture diagram
    - Document all API endpoints with examples
    - Provide quick start guides for each component
    - Document complete pipeline flow
    - Provide usage examples for command-line tools
    - Document training arguments and effects
    - Document how to add new models and judges
    - _Requirements: 25.1, 25.2, 25.3, 25.4, 25.5, 25.6, 25.7_
  
  - [ ] 19.2 Prepare deployment configuration
    - Document required environment variables
    - Provide Docker deployment instructions
    - Configure health check endpoints
    - Document production build process
    - _Requirements: 24.3, 24.4, 24.5, 24.6, 24.7_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples and edge cases
- The system uses Python for backend (Flask, PyTorch, boto3) and TypeScript/React for frontend
- All LLM interactions use Amazon Bedrock services (Claude Haiku, Claude Sonnet, Titan Embeddings)
