const API_BASE = '/api';

export interface KeywordMatchResult {
  matched_categories: Record<string, string[]>;
  matched_context: Record<string, unknown[]>;
  matched_dynamic_keywords: string[];
  match_score: number;
  has_match: boolean;
}

export interface ConclusionResult {
  is_scam: boolean | 'uncertain';
  confidence: number;
  scam_type: string | null;
  reasoning: string;
  red_flags: string[];
  advice: string;
  matched_news_event?: string;
  matched_tactic?: string;
  error?: string;
}

export interface VlmResult {
  extracted_text: string;
  urls: string[];
  phones: { country: string; number: string }[];
  image_type: string | null;
  sender: string | null;
  summary: string;
}

export interface ClassifierResult {
  label: 'scam' | 'legitimate';
  confidence: number;
  scam_probability: number;
  legitimate_probability: number;
}

export interface UrlCheckResult {
  url: string;
  score?: number;
  blacklisted?: boolean;
  phishing_count?: number;
  threat_count?: number;
  domain?: string;
  error?: string;
  source?: string;
}

export interface NumberCheckResult {
  number: string;
  country: string;
  name?: string;
  region?: string;
  spam_category?: string;
  error?: string;
}

export interface AnalysisResult {
  conclusion: ConclusionResult;
  keywordMatch: KeywordMatchResult;
  classifierResult?: ClassifierResult;
  urlResults?: UrlCheckResult[];
  numberResults?: NumberCheckResult[];
  vlm?: VlmResult;
}

async function post<T>(endpoint: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `API error ${res.status}`);
  }
  return res.json();
}

export async function analyzeText(text: string): Promise<AnalysisResult> {
  const [keywordMatch, classifierResult, urlCheck, numberCheck] = await Promise.all([
    post<KeywordMatchResult>('/keyword-check', { text }),
    post<ClassifierResult>('/classify', { text }),
    post<{ url_results: UrlCheckResult[] }>('/url-check', { text }).catch(() => ({ url_results: [] })),
    post<{ number_results: NumberCheckResult[] }>('/number-check', { text }).catch(() => ({ number_results: [] })),
  ]);
  const conclusion = await post<ConclusionResult>('/conclude', {
    user_input: text,
    keyword_match: keywordMatch,
    classifier_result: classifierResult,
    url_results: urlCheck.url_results,
    number_results: numberCheck.number_results,
  });
  return {
    conclusion,
    keywordMatch,
    classifierResult,
    urlResults: urlCheck.url_results,
    numberResults: numberCheck.number_results,
  };
}

export async function analyzeScreenshot(
  imageBase64: string,
  additionalText?: string,
): Promise<AnalysisResult> {
  const vlm = await post<VlmResult>('/vlm-analyze', { image_base64: imageBase64 });

  const combinedText = additionalText
    ? `${additionalText}\n\n${vlm.extracted_text}`
    : vlm.extracted_text;

  const urlsToCheck = vlm.urls.length > 0 ? vlm.urls : [];
  const phonesToCheck = vlm.phones.length > 0 ? vlm.phones : [];

  const [keywordMatch, classifierResult, urlCheck, numberCheck] = await Promise.all([
    post<KeywordMatchResult>('/keyword-check', { text: combinedText }),
    post<ClassifierResult>('/classify', { text: combinedText }),
    urlsToCheck.length > 0
      ? post<{ url_results: UrlCheckResult[] }>('/url-check', { urls: urlsToCheck })
      : post<{ url_results: UrlCheckResult[] }>('/url-check', { text: combinedText }).catch(() => ({ url_results: [] })),
    phonesToCheck.length > 0
      ? post<{ number_results: NumberCheckResult[] }>('/number-check', { phones: phonesToCheck })
      : post<{ number_results: NumberCheckResult[] }>('/number-check', { text: combinedText }).catch(() => ({ number_results: [] })),
  ]);

  const conclusion = await post<ConclusionResult>('/conclude', {
    user_input: combinedText,
    keyword_match: keywordMatch,
    classifier_result: classifierResult,
    url_results: urlCheck.url_results,
    number_results: numberCheck.number_results,
  });
  return {
    conclusion,
    keywordMatch,
    classifierResult,
    urlResults: urlCheck.url_results,
    numberResults: numberCheck.number_results,
    vlm,
  };
}

export async function scanUrl(url: string): Promise<AnalysisResult> {
  const [keywordMatch, classifierResult, urlCheck] = await Promise.all([
    post<KeywordMatchResult>('/keyword-check', { text: url }),
    post<ClassifierResult>('/classify', { text: url }),
    post<{ url_results: UrlCheckResult[] }>('/url-check', { urls: [url] }).catch(() => ({ url_results: [] })),
  ]);
  const conclusion = await post<ConclusionResult>('/conclude', {
    user_input: url,
    keyword_match: keywordMatch,
    classifier_result: classifierResult,
    url_results: urlCheck.url_results,
  });
  return {
    conclusion,
    keywordMatch,
    classifierResult,
    urlResults: urlCheck.url_results,
  };
}

export interface NewsArticle {
  title: string;
  url: string;
  source: string;
  published_at: string;
  risk_level: string;
  categories: string[];
  scam_tactics: string[];
  impersonation_targets: string[];
}

export interface NewsResponse {
  articles: NewsArticle[];
  total: number;
}

export async function fetchNews(): Promise<NewsResponse> {
  const res = await fetch(`${API_BASE}/news`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `API error ${res.status}`);
  }
  return res.json();
}
