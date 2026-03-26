import React from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  AlertCircle,
  ChevronRight,
  Eye,
  Phone,
  Link as LinkIcon,
  User,
  FileText,
} from 'lucide-react';
import { motion } from 'motion/react';
import { cn } from '../lib/utils';
import type { AnalysisResult as AnalysisResultType } from '../services/api';

interface Props {
  result: AnalysisResultType;
  onDismiss?: () => void;
}

function getRiskLevel(result: AnalysisResultType) {
  const { is_scam, confidence } = result.conclusion;
  if (is_scam === true) return 'danger';
  if (is_scam === 'uncertain' || (is_scam === false && confidence < 0.6)) return 'warning';
  return 'safe';
}

const riskConfig = {
  safe: {
    label: '安全',
    icon: ShieldCheck,
    bg: 'bg-primary-fixed',
    text: 'text-on-primary-fixed-variant',
    border: 'border-primary/20',
    bar: 'bg-primary',
    heroBg: 'bg-gradient-to-br from-primary-fixed to-primary-container',
    heroText: 'text-on-primary-fixed-variant',
  },
  warning: {
    label: '可疑',
    icon: AlertTriangle,
    bg: 'bg-tertiary-fixed',
    text: 'text-on-tertiary-fixed-variant',
    border: 'border-tertiary/20',
    bar: 'bg-tertiary',
    heroBg: 'bg-gradient-to-br from-tertiary-fixed to-tertiary-container',
    heroText: 'text-on-tertiary-fixed-variant',
  },
  danger: {
    label: '危險',
    icon: ShieldAlert,
    bg: 'bg-error-container',
    text: 'text-on-error-container',
    border: 'border-error/20',
    bar: 'bg-error',
    heroBg: 'bg-gradient-to-br from-error-container to-error',
    heroText: 'text-on-error-container',
  },
};

export default function AnalysisResult({ result, onDismiss }: Props) {
  const risk = getRiskLevel(result);
  const cfg = riskConfig[risk];
  const Icon = cfg.icon;
  const confidence = Math.round(result.conclusion.confidence * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 24, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="space-y-5"
    >
      {/* Hero risk banner */}
      <div className={cn('relative overflow-hidden rounded-2xl p-6', cfg.heroBg)}>
        <div className="absolute top-0 right-0 -translate-y-1/3 translate-x-1/4 w-40 h-40 bg-white/10 rounded-full blur-2xl" />
        <div className="relative z-10 flex items-center gap-5">
          <div className="w-16 h-16 rounded-2xl bg-white/15 backdrop-blur-md flex items-center justify-center">
            <Icon className={cn('w-9 h-9', cfg.heroText)} />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <span className={cn('px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider bg-white/20', cfg.heroText)}>
                {cfg.label}
              </span>
              {result.conclusion.scam_type && (
                <span className={cn('text-sm font-semibold opacity-80', cfg.heroText)}>
                  {result.conclusion.scam_type}
                </span>
              )}
            </div>
            <div className="flex items-center gap-3 mt-2">
              <div className="flex-1 h-2 bg-white/20 rounded-full overflow-hidden">
                <div
                  className={cn('h-full rounded-full transition-all duration-700', cfg.bar)}
                  style={{ width: `${confidence}%` }}
                />
              </div>
              <span className={cn('text-sm font-bold', cfg.heroText)}>
                {confidence}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* VLM extraction info (screenshots only) */}
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
        <div className={cn('rounded-xl p-5 space-y-2', cfg.bg, cfg.border, 'border')}>
          <h4 className={cn('font-headline font-bold', cfg.text)}>建議</h4>
          <p className={cn('text-sm leading-relaxed', cfg.text, 'opacity-90')}>{result.conclusion.advice}</p>
        </div>
      )}

      {/* Keyword match summary */}
      {result.keywordMatch.has_match && (
        <div className="bg-surface-container-low rounded-xl p-5 space-y-2">
          <h4 className="font-headline font-bold text-sm text-on-surface">
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
