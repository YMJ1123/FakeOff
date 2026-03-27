import React, { useState } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Eye,
  Phone,
  Link as LinkIcon,
  User,
  FileText,
  Search,
  Cpu,
  Globe,
  ChevronRight,
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../lib/utils';
import type { AnalysisResult as AnalysisResultType } from '../services/api';

interface Props {
  result: AnalysisResultType;
  onDismiss?: () => void;
}

interface SourceScore {
  label: string;
  icon: React.ElementType;
  score: number; // 0-100, 100=safe
  status: 'safe' | 'warning' | 'danger' | 'neutral';
  detail: string;
}

function computeSourceScores(result: AnalysisResultType): SourceScore[] {
  const sources: SourceScore[] = [];

  // 1. Keyword check
  const kw = result.keywordMatch;
  const kwRisk = kw.has_match ? Math.min(kw.match_score * 15, 100) : 0;
  const kwSafe = 100 - kwRisk;
  sources.push({
    label: '關鍵字',
    icon: Search,
    score: kwSafe,
    status: kwSafe >= 70 ? 'safe' : kwSafe >= 40 ? 'warning' : 'danger',
    detail: kw.has_match
      ? `命中 ${Object.keys(kw.matched_categories).length} 類（分數 ${kw.match_score}）`
      : '未命中任何風險關鍵字',
  });

  // 2. Scam Armor (ML Classifier)
  if (result.classifierResult) {
    const clf = result.classifierResult;
    const clfSafe = Math.round(clf.legitimate_probability * 100);
    sources.push({
      label: 'Scam Armor',
      icon: Cpu,
      score: clfSafe,
      status: clfSafe >= 70 ? 'safe' : clfSafe >= 40 ? 'warning' : 'danger',
      detail: `${clf.label === 'scam' ? '詐騙' : '合法'} ${Math.round(clf.confidence * 100)}%`,
    });
  }

  // 3. URL check
  const urls = result.urlResults ?? [];
  if (urls.length > 0) {
    const validUrls = urls.filter(u => u.score != null);
    if (validUrls.length > 0) {
      const avgScore = Math.round(validUrls.reduce((s, u) => s + (u.score ?? 100), 0) / validUrls.length);
      const hasBlacklist = urls.some(u => u.blacklisted);
      const hasPhishing = urls.some(u => (u.phishing_count ?? 0) > 0);
      const urlSafe = hasBlacklist ? Math.min(avgScore, 10) : hasPhishing ? Math.min(avgScore, 30) : avgScore;
      sources.push({
        label: '網址查詢',
        icon: Globe,
        score: urlSafe,
        status: urlSafe >= 70 ? 'safe' : urlSafe >= 40 ? 'warning' : 'danger',
        detail: hasBlacklist ? '含黑名單網址' : hasPhishing ? '含釣魚記錄' : `信任分數 ${avgScore}/100`,
      });
    }
  }

  // 4. Number check
  const nums = result.numberResults ?? [];
  if (nums.length > 0) {
    const hasSpam = nums.some(n => n.spam_category);
    const hasName = nums.some(n => n.name);
    const numSafe = hasSpam ? 15 : hasName ? 85 : 50;
    sources.push({
      label: '電話查詢',
      icon: Phone,
      score: numSafe,
      status: numSafe >= 70 ? 'safe' : numSafe >= 40 ? 'warning' : 'danger',
      detail: hasSpam
        ? `標記為 spam`
        : hasName
          ? `登記：${nums.find(n => n.name)?.name}`
          : '無登記資訊',
    });
  }

  return sources;
}

function computeCompositeScore(sources: SourceScore[]): number {
  if (sources.length === 0) return 50;
  const total = sources.reduce((s, src) => s + src.score, 0);
  return Math.round(total / sources.length);
}

const statusColor = {
  safe: { ring: 'stroke-primary', text: 'text-primary', bg: 'bg-primary-fixed', bgStrong: 'bg-primary' },
  warning: { ring: 'stroke-tertiary', text: 'text-tertiary', bg: 'bg-tertiary-fixed', bgStrong: 'bg-tertiary' },
  danger: { ring: 'stroke-error', text: 'text-error', bg: 'bg-error-container', bgStrong: 'bg-error' },
  neutral: { ring: 'stroke-outline', text: 'text-on-surface-variant', bg: 'bg-surface-container', bgStrong: 'bg-outline' },
};

function getOverallStatus(score: number): 'safe' | 'warning' | 'danger' {
  if (score >= 65) return 'safe';
  if (score >= 35) return 'warning';
  return 'danger';
}

const STATUS_LABEL = { safe: '低風險', warning: '中風險', danger: '高風險' };
const STATUS_ICON = { safe: ShieldCheck, warning: AlertTriangle, danger: ShieldAlert };

function ScoreRing({ score, status, size = 120 }: { score: number; status: 'safe' | 'warning' | 'danger'; size?: number }) {
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const colors = statusColor[status];

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-surface-container-high"
        />
        <motion.circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          className={colors.ring}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{ strokeDasharray: circumference }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={cn('text-3xl font-headline font-black', colors.text)}>{score}</span>
        <span className="text-[10px] font-bold text-on-surface-variant">/ 100</span>
      </div>
    </div>
  );
}

export default function AnalysisResult({ result, onDismiss }: Props) {
  const [expanded, setExpanded] = useState(false);
  const sources = computeSourceScores(result);
  const compositeScore = computeCompositeScore(sources);
  const overallStatus = getOverallStatus(compositeScore);
  const OverallIcon = STATUS_ICON[overallStatus];
  const colors = statusColor[overallStatus];

  return (
    <motion.div
      initial={{ opacity: 0, y: 24, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="space-y-5"
    >
      {/* Main score card */}
      <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-[0_8px_32px_rgba(0,0,0,0.06)]">
        <div className="flex items-center gap-6">
          <ScoreRing score={compositeScore} status={overallStatus} />

          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <OverallIcon className={cn('w-5 h-5', colors.text)} />
              <span className={cn('text-lg font-headline font-extrabold', colors.text)}>
                {STATUS_LABEL[overallStatus]}
              </span>
            </div>
            {result.conclusion.scam_type && (
              <span className={cn('inline-block px-3 py-1 rounded-full text-xs font-bold', colors.bg, colors.text)}>
                {result.conclusion.scam_type}
              </span>
            )}
            {result.conclusion.advice && (
              <p className="text-sm text-on-surface-variant leading-relaxed line-clamp-2">
                {result.conclusion.advice}
              </p>
            )}
          </div>
        </div>

        {/* 4 source indicators */}
        <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
          {sources.map((src) => {
            const sc = statusColor[src.status];
            return (
              <div key={src.label} className={cn('rounded-xl p-3 space-y-1.5', sc.bg)}>
                <div className="flex items-center gap-1.5">
                  <src.icon className={cn('w-3.5 h-3.5', sc.text)} />
                  <span className={cn('text-xs font-bold', sc.text)}>{src.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-white/40 rounded-full overflow-hidden">
                    <motion.div
                      className={cn('h-full rounded-full', sc.bgStrong)}
                      initial={{ width: 0 }}
                      animate={{ width: `${src.score}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut', delay: 0.3 }}
                    />
                  </div>
                  <span className={cn('text-[10px] font-bold', sc.text)}>{src.score}</span>
                </div>
                <p className={cn('text-[10px] leading-tight opacity-80', sc.text)}>{src.detail}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Expand/collapse button */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-center gap-2 bg-surface-container rounded-xl py-3 text-primary font-headline font-bold text-sm hover:bg-surface-container-high transition-colors"
      >
        {expanded ? '收合詳細分析' : '查看更多'}
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {/* Expanded detail section */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden space-y-5"
          >
            {/* VLM extraction info */}
            {result.vlm && (
              <div className="bg-surface-container-low rounded-xl p-5 space-y-3">
                <div className="flex items-center gap-2 text-on-surface font-headline font-bold text-sm">
                  <Eye className="w-4 h-4 text-primary" />
                  截圖分析結果
                </div>
                {result.vlm.sender && (
                  <div className="flex items-center gap-2 text-sm text-on-surface-variant">
                    <User className="w-4 h-4" />
                    <span className="font-semibold">來源：</span>{result.vlm.sender}
                  </div>
                )}
                {result.vlm.image_type && (
                  <div className="flex items-center gap-2 text-sm text-on-surface-variant">
                    <FileText className="w-4 h-4" />
                    <span className="font-semibold">類型：</span>{result.vlm.image_type}
                  </div>
                )}
                {result.vlm.extracted_text && (
                  <div className="bg-surface-container rounded-lg p-3 text-sm text-on-surface-variant leading-relaxed max-h-32 overflow-y-auto">
                    {result.vlm.extracted_text}
                  </div>
                )}
                {result.vlm.urls.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {result.vlm.urls.map((u, i) => (
                      <span key={i} className="inline-flex items-center gap-1 text-xs bg-surface-container px-2 py-1 rounded-lg text-primary">
                        <LinkIcon className="w-3 h-3" />{u}
                      </span>
                    ))}
                  </div>
                )}
                {result.vlm.phones.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {result.vlm.phones.map((p, i) => (
                      <span key={i} className="inline-flex items-center gap-1 text-xs bg-surface-container px-2 py-1 rounded-lg text-on-surface-variant">
                        <Phone className="w-3 h-3" />{p.number}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Reasoning */}
            {result.conclusion.reasoning && (
              <div className="bg-surface-container-lowest rounded-xl p-5 shadow-sm space-y-2">
                <h4 className="font-headline font-bold text-on-surface">分析說明</h4>
                <p className="text-sm text-on-surface-variant leading-relaxed">{result.conclusion.reasoning}</p>
              </div>
            )}

            {/* Red flags */}
            {result.conclusion.red_flags && result.conclusion.red_flags.length > 0 && (
              <div className="bg-surface-container-lowest rounded-xl p-5 shadow-sm space-y-3">
                <h4 className="font-headline font-bold text-on-surface flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-error" />
                  風險指標
                </h4>
                <ul className="space-y-2">
                  {result.conclusion.red_flags.map((flag, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-on-surface-variant">
                      <ChevronRight className="w-4 h-4 text-error mt-0.5 flex-shrink-0" />
                      {flag}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Advice */}
            {result.conclusion.advice && (
              <div className={cn('rounded-xl p-5 space-y-2 border', colors.bg, `border-${overallStatus === 'safe' ? 'primary' : overallStatus === 'warning' ? 'tertiary' : 'error'}/20`)}>
                <h4 className={cn('font-headline font-bold', colors.text)}>建議</h4>
                <p className={cn('text-sm leading-relaxed opacity-90', colors.text)}>{result.conclusion.advice}</p>
              </div>
            )}

            {/* Classifier detail */}
            {result.classifierResult && (
              <div className="bg-surface-container-low rounded-xl p-5 space-y-3">
                <h4 className="font-headline font-bold text-sm text-on-surface flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-primary" />
                  Scam Armor 分類器
                </h4>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex justify-between text-xs text-on-surface-variant mb-1">
                      <span>合法</span>
                      <span>詐騙</span>
                    </div>
                    <div className="h-3 bg-surface-container-high rounded-full overflow-hidden flex">
                      <div
                        className="h-full bg-primary rounded-l-full transition-all duration-500"
                        style={{ width: `${Math.round(result.classifierResult.legitimate_probability * 100)}%` }}
                      />
                      <div
                        className="h-full bg-error rounded-r-full transition-all duration-500"
                        style={{ width: `${Math.round(result.classifierResult.scam_probability * 100)}%` }}
                      />
                    </div>
                  </div>
                  <span className={cn(
                    "px-3 py-1 rounded-full text-xs font-bold",
                    result.classifierResult.label === 'scam'
                      ? 'bg-error-container text-on-error-container'
                      : 'bg-primary-fixed text-on-primary-fixed-variant'
                  )}>
                    {result.classifierResult.label === 'scam' ? '詐騙' : '合法'}
                    {' '}{Math.round(result.classifierResult.confidence * 100)}%
                  </span>
                </div>
              </div>
            )}

            {/* URL check details */}
            {result.urlResults && result.urlResults.length > 0 && (
              <div className="bg-surface-container-low rounded-xl p-5 space-y-3">
                <h4 className="font-headline font-bold text-sm text-on-surface flex items-center gap-2">
                  <Globe className="w-4 h-4 text-primary" />
                  網址風險查詢
                </h4>
                {result.urlResults.map((u, i) => (
                  <div key={i} className="bg-surface-container rounded-lg p-3 space-y-1">
                    <div className="text-xs text-primary font-mono truncate">{u.domain || u.url}</div>
                    {u.score != null ? (
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-2 bg-surface-container-high rounded-full overflow-hidden">
                          <div
                            className={cn(
                              'h-full rounded-full transition-all duration-500',
                              u.score >= 70 ? 'bg-primary' : u.score >= 40 ? 'bg-tertiary' : 'bg-error',
                            )}
                            style={{ width: `${u.score}%` }}
                          />
                        </div>
                        <span className={cn(
                          'text-xs font-bold',
                          u.score >= 70 ? 'text-primary' : u.score >= 40 ? 'text-tertiary' : 'text-error',
                        )}>
                          {u.score}/100
                        </span>
                      </div>
                    ) : u.error ? (
                      <span className="text-xs text-error">{u.error}</span>
                    ) : null}
                    <div className="flex flex-wrap gap-2 text-xs text-on-surface-variant">
                      {u.blacklisted && <span className="text-error font-bold">黑名單</span>}
                      {(u.phishing_count ?? 0) > 0 && <span className="text-error">釣魚記錄: {u.phishing_count}</span>}
                      {(u.threat_count ?? 0) > 0 && <span className="text-error">威脅記錄: {u.threat_count}</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Number check details */}
            {result.numberResults && result.numberResults.length > 0 && (
              <div className="bg-surface-container-low rounded-xl p-5 space-y-3">
                <h4 className="font-headline font-bold text-sm text-on-surface flex items-center gap-2">
                  <Phone className="w-4 h-4 text-primary" />
                  電話號碼查詢
                </h4>
                {result.numberResults.map((n, i) => (
                  <div key={i} className="bg-surface-container rounded-lg p-3 space-y-1">
                    <div className="text-xs font-mono text-on-surface">{n.number}</div>
                    <div className="flex flex-wrap gap-3 text-xs text-on-surface-variant">
                      {n.name && <span>登記名稱: {n.name}</span>}
                      {n.region && <span>地區: {n.region}</span>}
                      {n.spam_category && <span className="text-error font-bold">spam: {n.spam_category}</span>}
                      {n.error && <span className="text-error">{n.error}</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Keyword match details */}
            {result.keywordMatch.has_match && (
              <div className="bg-surface-container-low rounded-xl p-5 space-y-2">
                <h4 className="font-headline font-bold text-sm text-on-surface flex items-center gap-2">
                  <Search className="w-4 h-4 text-primary" />
                  關鍵字匹配（分數：{result.keywordMatch.match_score}）
                </h4>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(result.keywordMatch.matched_categories).map(([cat, keywords]) => (
                    <span
                      key={cat}
                      className="inline-flex items-center gap-1 text-xs bg-tertiary-fixed text-on-tertiary-fixed px-3 py-1 rounded-full font-semibold"
                    >
                      {cat}: {(keywords as string[]).join(', ')}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {onDismiss && (
        <button
          onClick={onDismiss}
          className="w-full text-center text-primary font-headline font-bold text-sm py-3 hover:underline"
        >
          重新分析
        </button>
      )}
    </motion.div>
  );
}
