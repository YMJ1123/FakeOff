const API_BASE = '/api';

export interface KeywordMatchResult {
  matched_categories: Record<string, string[]>;
  matched_context: Record<string, unknown[]>;
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

export interface AnalysisResult {
  conclusion: ConclusionResult;
  keywordMatch: KeywordMatchResult;
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
  const keywordMatch = await post<KeywordMatchResult>('/keyword-check', { text });
  const conclusion = await post<ConclusionResult>('/conclude', {
    user_input: text,
    keyword_match: keywordMatch,
  });
  return { conclusion, keywordMatch };
}

export async function analyzeScreenshot(
  imageBase64: string,
  additionalText?: string,
): Promise<AnalysisResult> {
  const vlm = await post<VlmResult>('/vlm-analyze', { image_base64: imageBase64 });

  const combinedText = additionalText
    ? `${additionalText}\n\n${vlm.extracted_text}`
    : vlm.extracted_text;

  const keywordMatch = await post<KeywordMatchResult>('/keyword-check', {
    text: combinedText,
  });
  const conclusion = await post<ConclusionResult>('/conclude', {
    user_input: combinedText,
    keyword_match: keywordMatch,
  });
  return { conclusion, keywordMatch, vlm };
}

export async function scanUrl(url: string): Promise<AnalysisResult> {
  const keywordMatch = await post<KeywordMatchResult>('/keyword-check', { text: url });
  const conclusion = await post<ConclusionResult>('/conclude', {
    user_input: url,
    keyword_match: keywordMatch,
  });
  return { conclusion, keywordMatch };
}
