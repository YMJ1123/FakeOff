import React, { useState, useRef, useCallback } from 'react';
import { 
  BrowserRouter as Router, 
  Routes, 
  Route, 
  NavLink, 
} from 'react-router-dom';
import { 
  Shield, 
  ShieldBan,
  Home,
  Newspaper,
  History,
  AlertTriangle, 
  AlertCircle,
  ArrowRight,
  ClipboardPaste,
  Image as ImageIcon,
  Lightbulb,
  Loader2,
  X,
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from './lib/utils';
import { analyzeText, analyzeScreenshot, type AnalysisResult as AnalysisResultType } from './services/api';
import AnalysisResultPanel from './components/AnalysisResult';

// --- Components ---

const BottomNav = () => {
  const navItems = [
    { icon: Home, label: '首頁', path: '/' },
    { icon: Newspaper, label: '時事', path: '/news' },
    { icon: History, label: '紀錄', path: '/record' },
    { icon: ShieldBan, label: '黑名單', path: '/blacklist' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 w-full z-50 bg-white/80 backdrop-blur-md border-t border-surface-container-high px-4 pb-8 pt-3 rounded-t-[2rem] shadow-[0_-4px_20px_rgba(0,0,0,0.03)]">
      <div className="flex justify-around items-center max-w-lg mx-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => cn(
              "flex flex-col items-center justify-center px-4 py-2 rounded-2xl transition-all duration-200 relative",
              isActive 
                ? "bg-secondary-container text-primary" 
                : "text-on-surface-variant hover:text-primary"
            )}
          >
            <item.icon className="w-6 h-6 mb-1" />
            <span className="text-[10px] font-headline font-bold uppercase tracking-wider">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
};

const Header = () => (
  <header className="fixed top-0 left-0 w-full z-50 bg-surface/80 backdrop-blur-md px-6 py-4 flex justify-between items-center border-b border-surface-container-high">
    <div className="flex items-center gap-2">
      <Shield className="w-6 h-6 text-primary fill-current" />
      <h1 className="text-xl font-headline font-extrabold tracking-tight text-primary">麥騙 FakeOff</h1>
    </div>
    <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-primary-container shadow-sm">
      <img 
        src="https://lh3.googleusercontent.com/aida-public/AB6AXuCfK44XcuZDEDirGoYHja2c373KRCxIqYDlDrUQ-LlxsqA5SThLNkRIjld7M2iRCqXjRi2QG7CXwEG7vpyMkNvLslWf_pmVkBokeRnoqxMLX907Qpfns1pJ9sOL2Qfi58osHLc-yjgeleRV-YBRiFJI86w_KbXY24se4HRBWdFuI7Ix05cCqVHc4kRGBsLNpyYWIFtyqBsPdqWjXVSWghXVh1B3OADdNgfyABX0_o5pn5T-heztuovxSAc7f6gaw-HaZwYJBkfn4L5u" 
        alt="Profile" 
        className="w-full h-full object-cover"
        referrerPolicy="no-referrer"
      />
    </div>
  </header>
);

// --- Screens ---

const MessagesScreen = () => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResultType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handlePaste = useCallback(async () => {
    try {
      const clipText = await navigator.clipboard.readText();
      if (clipText) setText(prev => prev + clipText);
    } catch {
      setError('無法讀取剪貼簿內容');
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setImagePreview(dataUrl);
      setImageBase64(dataUrl.split(',')[1]);
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!text.trim() && !imageBase64) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      let res: AnalysisResultType;
      if (imageBase64) {
        res = await analyzeScreenshot(imageBase64, text.trim() || undefined);
      } else {
        res = await analyzeText(text.trim());
      }
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : '分析失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  }, [text, imageBase64]);

  const handleDismiss = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  const clearImage = useCallback(() => {
    setImagePreview(null);
    setImageBase64(null);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-10 pb-12"
    >
      <header>
        <h1 className="text-4xl font-headline font-extrabold tracking-tight text-on-surface mb-2">分析訊息</h1>
        <p className="text-on-surface-variant font-medium">透過 AI 驅動的偵測技術，識別簡訊、電子郵件或螢幕截圖中的潛在詐騙。</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <section className="lg:col-span-8 space-y-6">
          <div className="bg-surface-container-lowest rounded-xl p-6 shadow-[0_12px_32px_rgba(24,28,32,0.04)]">
            <div className="flex items-center justify-between mb-4">
              <label className="font-headline font-bold text-lg text-on-surface">可疑文字</label>
              <button
                onClick={handlePaste}
                className="flex items-center gap-2 text-primary font-headline text-sm font-bold hover:opacity-80 transition-opacity"
              >
                <ClipboardPaste className="w-4 h-4" />
                貼上文字
              </button>
            </div>
            <textarea
              value={text}
              onChange={e => setText(e.target.value)}
              className="w-full min-h-[240px] bg-surface-container-low border-none rounded-xl p-4 text-on-surface focus:ring-2 focus:ring-primary/20 placeholder:text-on-surface-variant/50 font-body resize-none"
              placeholder="在此貼上簡訊、電子郵件或可疑訊息內容..."
            />

            {imagePreview && (
              <div className="mt-4 relative inline-block">
                <img src={imagePreview} alt="截圖預覽" className="max-h-40 rounded-xl border border-surface-container-high" />
                <button
                  onClick={clearImage}
                  className="absolute -top-2 -right-2 w-6 h-6 bg-error text-on-error rounded-full flex items-center justify-center shadow-md"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            <div className="mt-6 flex flex-col sm:flex-row gap-4">
              <button
                onClick={handleAnalyze}
                disabled={loading || (!text.trim() && !imageBase64)}
                className={cn(
                  "flex-1 flex items-center justify-center gap-2 bg-gradient-to-br from-primary to-primary-container text-on-primary font-headline font-bold py-4 px-8 rounded-full shadow-lg active:scale-95 transition-all duration-200",
                  (loading || (!text.trim() && !imageBase64)) && "opacity-50 cursor-not-allowed active:scale-100"
                )}
              >
                {loading && <Loader2 className="w-5 h-5 animate-spin" />}
                {loading ? '分析中...' : '分析詐騙'}
              </button>
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={loading}
                className="flex items-center justify-center gap-2 bg-surface-container-high text-primary font-headline font-bold py-4 px-8 rounded-full active:scale-95 transition-all duration-200"
              >
                <ImageIcon className="w-5 h-5" />
                上傳截圖
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
          </div>

          {error && (
            <div className="bg-error-container rounded-xl p-4 flex gap-3 items-center">
              <AlertCircle className="w-5 h-5 text-on-error-container flex-shrink-0" />
              <p className="text-on-error-container text-sm font-medium">{error}</p>
            </div>
          )}

          {result && (
            <AnalysisResultPanel result={result} onDismiss={handleDismiss} />
          )}

          {!result && (
            <div className="bg-secondary-container rounded-xl p-4 flex gap-4 items-start">
              <Lightbulb className="w-5 h-5 text-on-secondary-container mt-1" />
              <div>
                <p className="text-on-secondary-container text-sm font-semibold">專業提示</p>
                <p className="text-on-secondary-container/80 text-sm">為了獲得最佳結果，請包含原始訊息中發現的任何連結或電話號碼。</p>
              </div>
            </div>
          )}
        </section>

        <aside className="lg:col-span-4 space-y-6">
          <div className="bg-surface-container rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="font-headline font-bold text-lg">最近分析</h2>
              <History className="w-5 h-5 text-on-surface-variant cursor-pointer hover:text-primary" />
            </div>
            <div className="space-y-4">
              {[
                { time: '2 小時前', label: '威脅', color: 'bg-error-container text-on-error-container', text: '您的包裹遞送已暫停。請更新...' },
                { time: '昨天', label: '安全', color: 'bg-primary-fixed text-on-primary-fixed', text: '您的帳戶驗證碼為 482931...' },
                { time: '3 天前', label: '可疑', color: 'bg-tertiary-fixed text-on-tertiary-fixed', text: '緊急：偵測到您的銀行有異常登入嘗試...' },
              ].map((item, i) => (
                <div key={i} className="bg-surface-container-lowest p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer">
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">{item.time}</span>
                    <span className={cn("text-[10px] font-extrabold px-2 py-0.5 rounded-full", item.color)}>{item.label}</span>
                  </div>
                  <p className="text-sm font-medium line-clamp-2 text-on-surface">{item.text}</p>
                </div>
              ))}
            </div>
            <button className="w-full mt-6 text-primary font-headline text-sm font-bold flex items-center justify-center gap-2 hover:underline">
              查看完整歷史記錄
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </aside>
      </div>
    </motion.div>
  );
};

const NewsScreen = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    className="space-y-8 pb-12"
  >
    <header>
      <h1 className="text-4xl font-headline font-extrabold tracking-tight text-on-surface mb-2">詐騙時事</h1>
      <p className="text-on-surface-variant font-medium">最新詐騙手法與防範資訊，即時掌握社會動態。</p>
    </header>

    <div className="space-y-4">
      {[
        { title: '假冒銀行客服來電激增', date: '2026-03-25', tag: '電話詐騙', desc: '近期大量民眾反映接到假冒銀行客服的來電，聲稱帳戶異常需要驗證身份，藉此騙取個人資訊。' },
        { title: '投資詐騙新手法：AI 生成假名人代言', date: '2026-03-24', tag: '投資詐騙', desc: '詐騙集團利用 AI 深偽技術製作名人推薦投資的影片，在社群媒體大量散播吸引受害者。' },
        { title: '網購平台出現大量假商店', date: '2026-03-22', tag: '購物詐騙', desc: '多家電商平台發現假商店以超低價格吸引買家，收款後不出貨或寄送劣質品。' },
      ].map((item, i) => (
        <div key={i} className="bg-surface-container-lowest rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
          <div className="flex items-center gap-3 mb-3">
            <span className="px-3 py-1 bg-primary-fixed text-on-primary-fixed-variant text-xs font-bold rounded-full">{item.tag}</span>
            <span className="text-xs text-on-surface-variant">{item.date}</span>
          </div>
          <h3 className="text-lg font-headline font-bold text-on-surface mb-2">{item.title}</h3>
          <p className="text-on-surface-variant text-sm leading-relaxed">{item.desc}</p>
        </div>
      ))}
    </div>

    <div className="text-center py-8">
      <p className="text-on-surface-variant text-sm">更多時事資訊即將上線</p>
    </div>
  </motion.div>
);

const RecordScreen = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    className="space-y-8 pb-12"
  >
    <header>
      <h1 className="text-4xl font-headline font-extrabold tracking-tight text-on-surface mb-2">分析紀錄</h1>
      <p className="text-on-surface-variant font-medium">您過去的詐騙分析歷史記錄。</p>
    </header>

    <div className="space-y-4">
      {[
        { text: '您的包裹遞送已暫停。請更新...', time: '2 小時前', status: '威脅', color: 'bg-error-container text-on-error-container' },
        { text: '您的帳戶驗證碼為 482931...', time: '昨天', status: '安全', color: 'bg-primary-fixed text-on-primary-fixed' },
        { text: '緊急：偵測到您的銀行有異常登入嘗試...', time: '3 天前', status: '可疑', color: 'bg-tertiary-fixed text-on-tertiary-fixed' },
      ].map((item, i) => (
        <div key={i} className="bg-surface-container-lowest p-5 rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer flex items-center justify-between">
          <div className="flex-1 mr-4">
            <p className="font-medium text-on-surface line-clamp-1 mb-1">{item.text}</p>
            <p className="text-xs text-on-surface-variant">{item.time}</p>
          </div>
          <span className={cn("px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap", item.color)}>{item.status}</span>
        </div>
      ))}
    </div>

    <div className="text-center py-8">
      <p className="text-on-surface-variant text-sm">完整紀錄功能即將上線</p>
    </div>
  </motion.div>
);

const BlacklistScreen = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    className="space-y-8 pb-12"
  >
    <header>
      <h1 className="text-4xl font-headline font-extrabold tracking-tight text-on-surface mb-2">黑名單</h1>
      <p className="text-on-surface-variant font-medium">已知的詐騙號碼、網址與帳號，供您查詢比對。</p>
    </header>

    <div className="space-y-4">
      {[
        { value: '+886-9XX-XXX-123', type: '電話號碼', reports: 87, tag: '假冒客服' },
        { value: 'secure-bank-login.xyz', type: '網址', reports: 234, tag: '釣魚網站' },
        { value: 'invest_profit_tw', type: '社群帳號', reports: 56, tag: '投資詐騙' },
      ].map((item, i) => (
        <div key={i} className="bg-surface-container-lowest p-5 rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <ShieldBan className="w-5 h-5 text-error" />
              <span className="font-headline font-bold text-on-surface">{item.value}</span>
            </div>
            <span className="px-3 py-1 bg-error-container text-on-error-container text-xs font-bold rounded-full">{item.tag}</span>
          </div>
          <div className="flex items-center gap-4 text-xs text-on-surface-variant">
            <span>{item.type}</span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" />
              {item.reports} 次檢舉
            </span>
          </div>
        </div>
      ))}
    </div>

    <div className="text-center py-8">
      <p className="text-on-surface-variant text-sm">黑名單資料庫持續更新中</p>
    </div>
  </motion.div>
);

// --- Main App ---

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-surface">
        <Header />
        <main className="pt-24 px-6 max-w-5xl mx-auto pb-32">
          <AnimatePresence mode="wait">
            <Routes>
              <Route path="/" element={<MessagesScreen />} />
              <Route path="/news" element={<NewsScreen />} />
              <Route path="/record" element={<RecordScreen />} />
              <Route path="/blacklist" element={<BlacklistScreen />} />
            </Routes>
          </AnimatePresence>
        </main>
        <BottomNav />
      </div>
    </Router>
  );
}
