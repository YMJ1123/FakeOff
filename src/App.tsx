import React, { useState, useEffect } from 'react';
import { 
  BrowserRouter as Router, 
  Routes, 
  Route, 
  NavLink, 
  useLocation 
} from 'react-router-dom';
import { 
  Shield, 
  LayoutDashboard, 
  Link as LinkIcon, 
  Mail, 
  Bell, 
  ChevronRight, 
  Search, 
  AlertTriangle, 
  CheckCircle2, 
  Info, 
  ExternalLink,
  ShieldCheck,
  ArrowRight,
  MessageSquare,
  Flag,
  History,
  ClipboardPaste,
  Image as ImageIcon,
  Lightbulb,
  MapPin,
  TrendingDown,
  Globe,
  AlertCircle
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from './lib/utils';

// --- Components ---

const BottomNav = () => {
  const navItems = [
    { icon: LayoutDashboard, label: '狀態', path: '/' },
    { icon: LinkIcon, label: '連結', path: '/links' },
    { icon: Mail, label: '訊息', path: '/messages' },
    { icon: Bell, label: '警報', path: '/alerts', badge: true },
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
            <item.icon className={cn("w-6 h-6 mb-1", item.path === '/alerts' && "fill-current")} />
            <span className="text-[10px] font-headline font-bold uppercase tracking-wider">{item.label}</span>
            {item.badge && (
              <span className="absolute top-2 right-4 w-2 h-2 bg-error rounded-full border-2 border-white" />
            )}
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

const StatusScreen = () => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    className="space-y-8 pb-12"
  >
    {/* Protection Status Hero */}
    <section className="relative overflow-hidden rounded-[2.5rem] bg-gradient-to-br from-primary to-primary-container p-8 md:p-12 text-on-primary shadow-2xl">
      <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/4 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
      <div className="relative z-10 flex flex-col md:flex-row md:justify-between md:items-center gap-8">
        <div className="text-center md:text-left">
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/15 backdrop-blur-md text-sm font-semibold tracking-wide mb-6">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            實時防護已啟動
          </span>
          <h2 className="text-4xl md:text-6xl font-headline font-extrabold tracking-tighter mb-4 leading-tight">您已受保護</h2>
          <p className="text-on-primary-container text-lg max-w-md opacity-90">麥騙 FakeOff 正在主動監控您的連結與訊息。過去 24 小時內未偵測到威脅。</p>
        </div>
        <div className="flex-shrink-0 relative">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-48 h-48 rounded-full border border-white/10 animate-ping" />
            <div className="w-64 h-64 rounded-full border border-white/5 animate-pulse" />
          </div>
          <div className="relative w-32 h-32 md:w-40 md:h-40 rounded-full bg-white/10 backdrop-blur-xl border border-white/20 flex items-center justify-center shadow-inner">
            <ShieldCheck className="w-16 h-16 md:w-20 md:h-20 text-white fill-current" />
          </div>
        </div>
      </div>
    </section>

    {/* Quick Action Cards */}
    <section className="grid grid-cols-1 md:grid-cols-12 gap-6">
      <div className="md:col-span-8 bg-surface-container-low rounded-3xl p-8 flex flex-col justify-between group transition-all duration-300 hover:bg-surface-container-high cursor-pointer">
        <div>
          <div className="w-14 h-14 bg-primary rounded-2xl flex items-center justify-center text-white mb-6 shadow-lg shadow-primary/20">
            <LinkIcon className="w-8 h-8" />
          </div>
          <h3 className="text-2xl font-headline font-bold mb-2">掃描連結</h3>
          <p className="text-on-surface-variant leading-relaxed">在點擊之前，立即驗證網址是否安全、惡意或已知的釣魚網站。</p>
        </div>
        <div className="mt-8 flex items-center gap-4 text-primary font-bold">
          <span>分析目的地</span>
          <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-2" />
        </div>
      </div>

      <div className="md:col-span-4 bg-surface-container-lowest rounded-3xl p-8 shadow-sm transition-all duration-300 hover:shadow-md cursor-pointer border border-transparent hover:border-surface-tint/10">
        <div className="w-14 h-14 bg-secondary-container rounded-2xl flex items-center justify-center text-on-secondary-container mb-6">
          <Mail className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-headline font-bold mb-2">分析訊息</h3>
        <p className="text-on-surface-variant text-sm leading-relaxed mb-6">貼上來自簡訊或電子郵件的文字，以偵測可疑的語言模式。</p>
        <div className="h-1 bg-surface-container-high rounded-full overflow-hidden">
          <div className="h-full w-1/3 bg-primary rounded-full" />
        </div>
      </div>

      <div className="md:col-span-4 bg-tertiary-fixed rounded-3xl p-8 transition-all duration-300 hover:opacity-90 cursor-pointer">
        <div className="w-14 h-14 bg-on-tertiary-fixed rounded-2xl flex items-center justify-center text-white mb-6">
          <Flag className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-headline font-bold text-on-tertiary-fixed mb-2">檢舉詐騙</h3>
        <p className="text-on-tertiary-fixed-variant text-sm leading-relaxed">透過標記新的可疑活動來幫助社群。</p>
      </div>

      <div className="md:col-span-8 bg-surface-container-low rounded-3xl p-8 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex -space-x-4">
            <img className="w-12 h-12 rounded-full border-4 border-surface-container-low" src="https://lh3.googleusercontent.com/aida-public/AB6AXuATa0G-SOocFaFzhsIuqZRZlaORh3_Jy6JxndFomegnPenkHgak7gDMMjwhrH0BKsaXq_K0fXFrsn1t3e_A3LfI3qmp_XSGcs0nPiC0w-HQd5S7BPIgY09nSv0jbU7zGV2cvuAyB5NF4rPzNQ9QorXUOgo2ff9nXG_oH8q0vnktSV53dgjcFrDvv9OeLbv-0X_QhHcR90LVGgYF998y7arvBk4b6RN6fXuUqa0VzRZ6FXBS6GBfswEA65jtPW4byucHNK0ok9-k5FbE" alt="User" referrerPolicy="no-referrer" />
            <img className="w-12 h-12 rounded-full border-4 border-surface-container-low" src="https://lh3.googleusercontent.com/aida-public/AB6AXuC4m7dXevob_ga2fBQQeZHcvTdyCEPhDaBkuZZ8zyu6dsGFPx3nxpiNJe3OdtdiTqeFx1KL17mOio1sFTnXgk1dHWglD4TPjvuGQ4jVTSVJTK_sp38yIBdjVSlWcGuqbLWMB0aBkkwwVUCXNpvaVe9GzzjZgTylqAyTnjBpHigIRbEbTmzPGu0T3OT5FOAGQiDwYSO4NvmwzTckl-q4ChnKsxCgi7x1lHD5W7W5_G0OYgwuJKLSpANeUmvivl0FgZN2nW_gaY47uHyY" alt="User" referrerPolicy="no-referrer" />
            <div className="w-12 h-12 rounded-full border-4 border-surface-container-low bg-surface-container-highest flex items-center justify-center text-xs font-bold text-on-surface-variant">+42</div>
          </div>
          <div>
            <h4 className="font-bold">社群信任</h4>
            <p className="text-sm text-on-surface-variant">今日已解除 442 個新威脅。</p>
          </div>
        </div>
        <button className="bg-primary text-on-primary px-6 py-3 rounded-full font-bold text-sm tracking-wide hover:bg-primary-container transition-colors">查看動態</button>
      </div>
    </section>

    {/* Recent Scans */}
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-headline font-bold tracking-tight">最近掃描</h3>
        <button className="text-primary font-bold text-sm flex items-center gap-1 hover:underline">
          查看全部 <ChevronRight className="w-4 h-4" />
        </button>
      </div>
      <div className="bg-surface-container-low rounded-[2rem] overflow-hidden">
        <div className="divide-y divide-surface-variant/30">
          {[
            { title: 'https://bank-secure-auth.net', time: '2 小時前', type: '網址掃描', status: '安全', color: 'bg-primary-fixed text-on-primary-fixed-variant' },
            { title: 'SMS: "Unusual activity on your..."', time: '5 小時前', type: '訊息分析', status: '可疑', color: 'bg-tertiary-fixed text-on-tertiary-fixed-variant' },
            { title: 'http://win-giftcard-now.phish', time: '昨天', type: '網址掃描', status: '威脅', color: 'bg-error-container text-on-error-container' },
          ].map((item, i) => (
            <div key={i} className="p-6 flex items-center justify-between hover:bg-surface-container-high transition-colors cursor-pointer">
              <div className="flex items-center gap-5">
                <div className={cn("w-12 h-12 rounded-2xl flex items-center justify-center", item.status === 'SAFE' ? 'bg-primary-fixed' : item.status === 'SUSPICIOUS' ? 'bg-tertiary-fixed' : 'bg-error-container')}>
                  {item.type.includes('URL') ? <LinkIcon className="w-6 h-6" /> : <AlertTriangle className="w-6 h-6" />}
                </div>
                <div>
                  <h4 className="font-bold text-on-surface">{item.title}</h4>
                  <p className="text-xs text-on-surface-variant uppercase tracking-widest font-semibold mt-1">{item.time} • {item.type}</p>
                </div>
              </div>
              <span className={cn("px-4 py-1.5 rounded-full text-xs font-bold", item.color)}>{item.status}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  </motion.div>
);

const LinksScreen = () => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    className="space-y-12 pb-12"
  >
    <section className="space-y-6">
      <div className="space-y-2">
        <p className="text-primary font-headline font-bold uppercase tracking-widest text-xs">安全模組</p>
        <h2 className="text-4xl md:text-5xl font-headline font-extrabold text-on-surface tracking-tight">連結/網址掃描器</h2>
        <p className="text-on-surface-variant max-w-lg">在點擊之前，立即驗證任何網址的完整性。我們的麥騙引擎會解析重新導向和釣魚模式。</p>
      </div>
      <div className="relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-primary to-primary-container rounded-2xl blur opacity-10 group-focus-within:opacity-25 transition duration-500" />
        <div className="relative flex flex-col md:flex-row gap-4">
          <div className="flex-grow bg-surface-container-low rounded-xl px-4 py-4 flex items-center gap-4 transition-all duration-300 focus-within:bg-surface-container-highest">
            <LinkIcon className="w-6 h-6 text-on-surface-variant" />
            <input 
              type="text" 
              placeholder="https://example.com/secure-path" 
              className="w-full bg-transparent border-none focus:ring-0 text-on-surface placeholder:text-on-surface-variant/50 font-medium"
            />
          </div>
          <button className="bg-gradient-to-br from-primary to-primary-container text-on-primary px-8 py-4 rounded-full font-headline font-bold text-lg shadow-lg active:scale-95 transition-transform">
            立即掃描
          </button>
        </div>
      </div>
    </section>

    <section className="space-y-8">
      <div className="flex items-end justify-between">
        <h3 className="text-2xl font-headline font-bold">運作原理</h3>
        <span className="text-sm font-headline font-semibold text-primary cursor-pointer hover:underline">進階協定</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { icon: Globe, title: '全球黑名單', desc: '交叉比對超過 50 個實時威脅資料庫，包括 Google 安全瀏覽和 PhishTank。' },
          { icon: TrendingDown, title: '釣魚偵測', desc: '分析網址字串和頁面元數據，以防範同形異義字攻擊和可疑的重新導向迴圈。' },
          { icon: Shield, title: '沙盒掃描', desc: '連結會由我們的安全虛擬瀏覽器訪問，以偵測零時差漏洞和隱蔽式下載。' },
        ].map((item, i) => (
          <div key={i} className="bg-surface-container-low p-8 rounded-xl space-y-4 hover:bg-surface-container-high transition-colors">
            <div className="w-12 h-12 rounded-full bg-primary-fixed flex items-center justify-center">
              <item.icon className="w-6 h-6 text-primary" />
            </div>
            <h4 className="font-headline font-bold text-lg">{item.title}</h4>
            <p className="text-on-surface-variant text-sm leading-relaxed">{item.desc}</p>
          </div>
        ))}
      </div>
    </section>

    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-headline font-bold">最近網路活動</h3>
        <button className="text-primary font-headline text-sm font-bold flex items-center gap-1 hover:underline">
          查看全部 <ChevronRight className="w-4 h-4" />
        </button>
      </div>
      <div className="space-y-3">
        {[
          { url: 'portal.my-banking.com', time: '2 分鐘前', status: '已驗證安全', type: 'SAFE' },
          { url: 'bit.ly/secure-prize-claim', time: '15 分鐘前', status: '可疑', type: 'SUSPICIOUS' },
          { url: 'amazon-login-update.net', time: '1 小時前', status: '惡意', type: 'MALICIOUS' },
          { url: 'docs.google.com', time: '3 小時前', status: '已驗證安全', type: 'SAFE' },
        ].map((item, i) => (
          <div key={i} className="bg-surface-container-lowest p-5 rounded-xl flex items-center justify-between shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-surface-container flex items-center justify-center">
                <Globe className="w-5 h-5 text-on-surface-variant" />
              </div>
              <div>
                <p className="font-headline font-bold text-on-surface">{item.url}</p>
                <p className="text-xs text-on-surface-variant">Scanned {item.time} • {i % 2 === 0 ? '0' : '3'} redirects</p>
              </div>
            </div>
            <div className={cn(
              "flex items-center gap-2 px-4 py-1.5 rounded-full font-bold text-xs uppercase tracking-tighter",
              item.type === 'SAFE' ? "bg-primary-fixed text-on-primary-fixed-variant" : 
              item.type === 'SUSPICIOUS' ? "bg-tertiary-fixed text-on-tertiary-fixed" : 
              "bg-error-container text-on-error-container"
            )}>
              {item.type === 'SAFE' ? <CheckCircle2 className="w-3 h-3" /> : item.type === 'SUSPICIOUS' ? <AlertTriangle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
              {item.status}
            </div>
          </div>
        ))}
      </div>
    </section>
  </motion.div>
);

const MessagesScreen = () => (
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
            <button className="flex items-center gap-2 text-primary font-headline text-sm font-bold hover:opacity-80 transition-opacity">
              <ClipboardPaste className="w-4 h-4" />
              貼上文字
            </button>
          </div>
          <textarea 
            className="w-full min-h-[240px] bg-surface-container-low border-none rounded-xl p-4 text-on-surface focus:ring-2 focus:ring-primary/20 placeholder:text-on-surface-variant/50 font-body resize-none" 
            placeholder="在此貼上簡訊、電子郵件或可疑訊息內容..."
          />
          <div className="mt-6 flex flex-col sm:flex-row gap-4">
            <button className="flex-1 bg-gradient-to-br from-primary to-primary-container text-on-primary font-headline font-bold py-4 px-8 rounded-full shadow-lg active:scale-95 transition-all duration-200">
              分析詐騙
            </button>
            <button className="flex items-center justify-center gap-2 bg-surface-container-high text-primary font-headline font-bold py-4 px-8 rounded-full active:scale-95 transition-all duration-200">
              <ImageIcon className="w-5 h-5" />
              上傳截圖
            </button>
          </div>
        </div>

        <div className="bg-secondary-container rounded-xl p-4 flex gap-4 items-start">
          <Lightbulb className="w-5 h-5 text-on-secondary-container mt-1" />
          <div>
            <p className="text-on-secondary-container text-sm font-semibold">專業提示</p>
            <p className="text-on-secondary-container/80 text-sm">為了獲得最佳結果，請包含原始訊息中發現的任何連結或電話號碼。</p>
          </div>
        </div>
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

const AlertsScreen = () => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    className="space-y-12 pb-12"
  >
    <section className="space-y-2">
      <h1 className="text-4xl font-headline font-extrabold tracking-tight text-on-surface">詐騙警報</h1>
      <p className="text-on-surface-variant font-medium">針對您社群威脅的實時情報。</p>
    </section>

    <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2 relative overflow-hidden rounded-xl bg-surface-container-lowest shadow-[0_12px_32px_rgba(24,28,32,0.06)] group">
        <div className="p-6 pb-2 flex justify-between items-center relative z-10 bg-white/60 backdrop-blur-sm">
          <h2 className="text-xl font-headline font-bold">您所在地區的最近詐騙</h2>
          <span className="px-3 py-1 bg-primary text-on-primary text-xs font-bold rounded-full">實時地圖</span>
        </div>
        <div className="h-[300px] w-full relative">
          <img 
            className="w-full h-full object-cover brightness-95" 
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuDWtWMCJsVqKRtrzSS07YSKukBq05XuAbu4qaIr7Xl4KUQoq2INYKNbno34jxGmA2WsVc4FCZoSluxTro4VRAqfPB2YkeIQtaNhb6AEhZRFg1iYHresf9ipC19Ef4OSbSjNY8jNdl0N-r_aiZ06tTKAMDpyCtJe3mL3kswDeGxWHfkGM71CNDwGtZYUtOz9ua1DdYQ_ccHW4AAJu1eN144WGM2rDcVTf1ZCRMRjeRr_YS6HmUdrYUmW5TzB6gaa0yWL707Wlx3ku_pW" 
            alt="Map"
            referrerPolicy="no-referrer"
          />
          <div className="absolute top-1/3 left-1/4 animate-pulse">
            <MapPin className="text-error w-8 h-8 fill-current" />
          </div>
          <div className="absolute bottom-1/4 right-1/3">
            <MapPin className="text-tertiary w-6 h-6 fill-current" />
          </div>
        </div>
        <div className="p-4 bg-surface-container-low flex items-center gap-4">
          <MapPin className="w-5 h-5 text-primary" />
          <span className="text-sm font-semibold text-on-surface-variant">正在監控舊金山 Market St 附近的活動</span>
        </div>
      </div>

      <div className="bg-primary-container text-on-primary-container p-8 rounded-xl flex flex-col justify-between overflow-hidden relative">
        <div className="relative z-10">
          <span className="text-xs font-bold uppercase tracking-widest opacity-80">每週威脅等級</span>
          <div className="text-6xl font-headline font-extrabold mt-2">低</div>
          <p className="mt-4 text-sm leading-relaxed opacity-90">與上週相比，本地報告下降了 12%。請保持基本警惕。</p>
        </div>
        <div className="mt-8 space-y-3 relative z-10">
          <div className="flex justify-between items-center text-sm border-b border-white/10 pb-2">
            <span>釣魚攻擊次數</span>
            <span className="font-bold">24</span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span>報告損失</span>
            <span className="font-bold">$1.2k</span>
          </div>
        </div>
        <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-white/10 rounded-full blur-2xl" />
      </div>
    </section>

    <section className="space-y-6">
      <div className="flex justify-between items-end">
        <h2 className="text-2xl font-headline font-bold tracking-tight">安全提示與教育</h2>
        <button className="text-primary font-bold text-sm hover:underline">查看所有指南</button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          { icon: Mail, title: '識別釣魚', bg: 'bg-tertiary-fixed', color: 'text-on-tertiary-fixed', desc: '在點擊任何連結之前，了解可疑電子郵件和簡訊的危險信號。' },
          { icon: ShieldCheck, title: '身份保護', bg: 'bg-secondary-container', color: 'text-on-secondary-container', desc: '採取實際步驟保護您的社會安全號碼和信用檔案，免受複雜的身份竊賊侵害。' },
          { icon: Shield, title: '安全購物', bg: 'bg-primary-fixed', color: 'text-on-primary-fixed', desc: '在瀏覽線上市場和社交廣告時，保護您的財務細節。' },
        ].map((item, i) => (
          <div key={i} className="bg-surface-container-lowest rounded-xl p-6 transition-all hover:-translate-y-1 hover:shadow-[0_12px_32px_rgba(24,28,32,0.06)] flex flex-col group">
            <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center mb-6", item.bg)}>
              <item.icon className={cn("w-6 h-6", item.color)} />
            </div>
            <h3 className="text-lg font-headline font-bold mb-2">{item.title}</h3>
            <p className="text-on-surface-variant text-sm flex-grow mb-6">{item.desc}</p>
            <button className="w-full py-3 bg-surface-container-high text-primary font-bold rounded-full text-sm group-hover:bg-primary group-hover:text-on-primary transition-colors">開始閱讀</button>
          </div>
        ))}
      </div>
    </section>

    <section className="bg-surface-container-high rounded-3xl p-8 flex flex-col md:flex-row items-center gap-8 overflow-hidden relative">
      <div className="flex-grow space-y-4">
        <h2 className="text-3xl font-headline font-extrabold tracking-tight">發現可疑事物？</h2>
        <p className="text-on-surface-variant max-w-md">您的檢舉能幫助 麥騙 FakeOff 網路中的數千名使用者。只需幾秒鐘即可安全地標記潛在詐騙。</p>
        <button className="px-8 py-3 bg-gradient-to-br from-primary to-primary-container text-on-primary font-bold rounded-full shadow-lg shadow-primary/20 active:scale-95 transition-all">檢舉詐騙</button>
      </div>
      <div className="w-full md:w-1/3 flex justify-center">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/10 rounded-full blur-3xl scale-150" />
          <AlertCircle className="w-32 h-32 text-primary-container relative z-10" />
        </div>
      </div>
    </section>
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
              <Route path="/" element={<StatusScreen />} />
              <Route path="/links" element={<LinksScreen />} />
              <Route path="/messages" element={<MessagesScreen />} />
              <Route path="/alerts" element={<AlertsScreen />} />
            </Routes>
          </AnimatePresence>
        </main>
        <BottomNav />
      </div>
    </Router>
  );
}
