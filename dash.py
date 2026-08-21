import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, BarChart2, Clock, Users, Zap, Shield, 
  Crosshair, AlertTriangle, CheckCircle, TrendingUp, TrendingDown,
  Cpu, Droplet, Wind, Sun, Maximize2, ArrowUpRight, ArrowDownRight,
  MessageSquare, X, Send, Sparkles, Bot, Leaf, Network
} from 'lucide-react';

const COLORS = {
  bg: '#0B0E14',
  panel: 'rgba(18, 24, 38, 0.65)',
  panelBorder: 'rgba(255, 255, 255, 0.08)',
  gold: '#F59E0B',
  silver: '#06B6D4',
  success: '#10B981',
  invalid: '#F43F5E',
  textMain: '#FFFFFF',
  textMuted: '#94A3B8'
};

const BOTS_DATA = [
  { id: 1, name: 'Golden Wing', asset: 'XAU/USD', status: 'active', rTarget: '+2.5R', ev: '0.85', atr: '14.2', sparkline: [10, 15, 12, 25, 22, 30, 45, 40] },
  { id: 2, name: 'Mean Reversion', asset: 'XAG/USD', status: 'standby', rTarget: '+1.2R', ev: '0.45', atr: '0.4', sparkline: [20, 22, 21, 23, 20, 18, 19, 21] },
  { id: 3, name: 'Liquidity Sweep', asset: 'XAU/USD', status: 'analyzing', rTarget: '+3.0R', ev: '0.65', atr: '16.1', sparkline: [5, 10, 8, 15, 12, 20, 18, 25] },
  { id: 4, name: 'Asian Range Breakout', asset: 'XAG/USD', status: 'standby', rTarget: '+1.5R', ev: '0.35', atr: '0.3', sparkline: [15, 15, 14, 16, 15, 15, 14, 16] },
  { id: 5, name: 'Macro Event Fade', asset: 'XAU/USD', status: 'active', rTarget: '+4.0R', ev: '1.20', atr: '22.5', sparkline: [0, 5, -2, 10, 8, 25, 20, 40] },
];

const TIMELINE_EVENTS = [
  { time: '09:00', label: 'Открытие Лондона', desc: 'Набор ликвидности' },
  { time: '15:30', label: 'CPI (США)', desc: 'Высокая волатильность' },
  { time: '17:00', label: 'Открытие NY', desc: 'Смена тренда' },
  { time: '20:00', label: 'Фиксинг', desc: 'Снижение объемов' },
];

const GlassCard = ({ children, className = '', glowColor = 'transparent', onClick }) => {
  return (
    <div 
      onClick={onClick}
      className={`relative overflow-hidden rounded-2xl backdrop-blur-xl ${className}`}
      style={{
        backgroundColor: COLORS.panel,
        border: `1px solid ${COLORS.panelBorder}`,
        boxShadow: `0 8px 32px 0 rgba(0, 0, 0, 0.3), inset 0 1px 0 0 rgba(255,255,255,0.05), 0 0 20px ${glowColor}`,
        transition: 'all 0.3s ease'
      }}
    >
      {children}
    </div>
  );
};

const SparklineChart = ({ data, color, isQuant }) => {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - (((val - min) / range) * 80 + 10); // 10% padding
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="relative w-full h-12">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-full overflow-visible">
        {/* Soft glow under the line */}
        <polyline points={`${points} 100,100 0,100`} fill={`${color}20`} opacity="0.5" />
        <polyline 
          points={points} 
          fill="none" 
          stroke={color} 
          strokeWidth="3" 
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{ filter: `drop-shadow(0px 2px 4px ${color}80)` }}
        />
      </svg>
      {isQuant && (
        <div className="absolute top-0 right-0 text-[10px] text-gray-400 font-mono">
          Max: {max.toFixed(1)}
        </div>
      )}
    </div>
  );
};

const GlobalHealthBar = ({ isQuant }) => {
  const [period, setPeriod] = useState('allTime');

  // Моковые данные для очков по разным периодам
  const scoreData = {
    week: { val: '+120', curve: [50, 40, 60, 50, 80, 100, 120], winrate: '71.4%' },
    month: { val: '+450', curve: [100, 150, 120, 250, 220, 300, 450], winrate: '68.2%' },
    allTime: { val: '12 450', curve: [1000, 2500, 4000, 3500, 6000, 9000, 12450], winrate: '65.8%' }
  };

  const current = scoreData[period];
  
  return (
    <GlassCard className="p-6 col-span-full mb-6">
      <div className="flex flex-col md:flex-row items-center justify-between gap-6">
        
        {/* Main Stat - Yasno Score */}
        <div className="flex-1 w-full">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-2 gap-3 sm:gap-0">
            <div className="flex items-center gap-3">
              <div className="text-sm text-slate-400 font-medium tracking-wide uppercase">Yasno Score (Рейтинг)</div>
              {/* Легенда начисления очков */}
              <div className="text-[10px] text-slate-500 bg-white/5 px-2 py-0.5 rounded border border-white/10 flex items-center gap-1.5 hidden sm:flex">
                <span className="text-emerald-400 font-bold">+10 <span className="font-normal text-slate-400">успех</span></span> 
                <span className="text-slate-600">|</span>
                <span className="text-rose-400 font-bold">-10 <span className="font-normal text-slate-400">ошибка</span></span>
              </div>
            </div>
            
            {/* Переключатель периодов */}
            <div className="flex bg-black/40 p-1 rounded-lg border border-white/10 self-start sm:self-auto w-full sm:w-auto">
              <button 
                onClick={() => setPeriod('week')} 
                className={`flex-1 sm:flex-none px-3 py-1 text-xs rounded-md transition-all ${period === 'week' ? 'bg-white/15 text-white shadow-[0_0_10px_rgba(255,255,255,0.05)] border border-white/10' : 'text-slate-400 hover:text-white border border-transparent'}`}
              >
                Неделя
              </button>
              <button 
                onClick={() => setPeriod('month')} 
                className={`flex-1 sm:flex-none px-3 py-1 text-xs rounded-md transition-all ${period === 'month' ? 'bg-white/15 text-white shadow-[0_0_10px_rgba(255,255,255,0.05)] border border-white/10' : 'text-slate-400 hover:text-white border border-transparent'}`}
              >
                Месяц
              </button>
              <button 
                onClick={() => setPeriod('allTime')} 
                className={`flex-1 sm:flex-none px-3 py-1 text-xs rounded-md transition-all ${period === 'allTime' ? 'bg-white/15 text-white shadow-[0_0_10px_rgba(255,255,255,0.05)] border border-white/10' : 'text-slate-400 hover:text-white border border-transparent'}`}
              >
                Всё время
              </button>
            </div>
          </div>

          <div className="flex items-end gap-3 mt-3">
            <span className="text-4xl sm:text-5xl font-bold text-white tracking-tight flex items-center gap-2">
              <Sparkles className="text-amber-400" size={32} style={{ filter: 'drop-shadow(0 0 8px rgba(245, 158, 11, 0.6))' }} />
              {current.val} <span className="text-amber-400/80 text-xl sm:text-2xl font-medium">pts</span>
            </span>
            {isQuant && <span className="text-sm text-emerald-500 mb-1.5 font-mono">Winrate: {current.winrate}</span>}
          </div>
          <div className="mt-5">
            <SparklineChart data={current.curve} color={COLORS.gold} isQuant={isQuant} />
          </div>
        </div>

        {/* Gauge Chart & Stats */}
        <div className="flex gap-8 w-full md:w-auto border-t md:border-t-0 md:border-l border-white/10 pt-4 md:pt-0 md:pl-8">
          <div className="flex flex-col items-center">
            <div className="relative w-20 h-20">
              <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
                <path className="text-white/10" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" />
                <path className="text-emerald-400" strokeDasharray="69.4, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" style={{ filter: 'drop-shadow(0 0 4px rgba(16, 185, 129, 0.6))' }} />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center text-white font-bold text-sm">
                69%
              </div>
            </div>
            <span className="text-xs text-slate-400 mt-2 text-center w-24">Точность<br/>паттернов</span>
          </div>

          <div className="flex flex-col justify-center gap-3">
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <CheckCircle size={16} className="text-emerald-400" />
              <span>1 240+ проверок</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <Cpu size={16} className="text-amber-400" />
              <span>5 активных ботов</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <Shield size={16} className="text-blue-400" />
              <span>0 скрытых ошибок</span>
            </div>
          </div>
        </div>

      </div>
    </GlassCard>
  );
};

const MarketRadar = ({ isQuant }) => {
  const [activeAsset, setActiveAsset] = useState('Golden Wing (XAU)');
  const [goldBias, setGoldBias] = useState('bullish'); // 'bullish' | 'bearish'

  const ASSET_DATA = {
    'Golden Wing (XAU)': {
      state: 'storm',
      color: goldBias === 'bullish' ? COLORS.success : COLORS.invalid,
      shadowGlow: goldBias === 'bullish' ? 'rgba(16, 185, 129, 0.4)' : 'rgba(244, 63, 94, 0.4)',
      gradStart: goldBias === 'bullish' ? '#34D399' : '#FDA4AF',
      icon: goldBias === 'bullish' ? ArrowUpRight : ArrowDownRight,
      label: goldBias === 'bullish' ? 'ВОСХОДЯЩИЙ ШТОРМ' : 'НИСХОДЯЩИЙ ШТОРМ',
      biasText: goldBias === 'bullish' ? 'Бычий настрой' : 'Медвежий настрой',
      volatility: 'Высокая волатильность',
      atr: '18.5',
      tag: goldBias === 'bullish' ? 'Лонг / Покупки' : 'Шорт / Продажи',
      descQuant: goldBias === 'bullish' 
        ? 'Фокус: Пробой H4 FVG вверх. Игнор шорт-сигналов. Макс. просадка: 0.8%' 
        : 'Фокус: Слом структуры на 15m. Ищем вход от шортового OB. Макс. просадка: 0.8%',
      descSimple: goldBias === 'bullish' 
        ? 'Фокус: Ищем покупки на откатах. Мощный попутный ветер.' 
        : 'Фокус: Ищем продажи на коррекциях. Сильное давление продавцов.'
    },
    'Silver Base (XAG)': {
      state: 'calm',
      color: COLORS.silver,
      shadowGlow: 'rgba(6, 182, 212, 0.4)',
      gradStart: '#A5F3FC',
      icon: Droplet,
      label: 'ШТИЛЬ (ТУМАН)',
      biasText: 'Нейтральный (Боковик)',
      volatility: 'Низкая волатильность',
      atr: '0.35',
      tag: 'Коридор / Флэт',
      descQuant: 'Фокус: Отскоки Bollinger Bands. R-множитель: 1.2',
      descSimple: 'Фокус: Торговля от границ канала. Ждем выхода из диапазона.'
    }
  };

  const current = ASSET_DATA[activeAsset];
  const IconComponent = current.icon;

  return (
    <GlassCard className="p-6 flex flex-col h-full">
      {}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Crosshair size={20} className="text-slate-400"/>
          Радар "Погода рынка"
        </h2>
      </div>

      {}
      <div className="flex bg-black/40 p-1 rounded-lg border border-white/10 mb-4 w-full">
        {Object.keys(ASSET_DATA).map(asset => (
          <button
            key={asset}
            onClick={() => setActiveAsset(asset)}
            className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-all duration-300 ${
              activeAsset === asset 
                ? 'bg-white/15 text-white shadow-[0_0_10px_rgba(255,255,255,0.05)] border border-white/10' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
            }`}
          >
            {asset}
          </button>
        ))}
      </div>

      {/* Bias Switcher (Only visible for Golden Wing) */}
      <div className={`flex justify-center transition-all duration-300 overflow-hidden ${activeAsset === 'Golden Wing (XAU)' ? 'h-8 opacity-100 mb-4' : 'h-0 opacity-0 mb-0'}`}>
        <div className="flex bg-white/5 p-0.5 rounded-full border border-white/10">
          <button 
            onClick={() => setGoldBias('bullish')}
            className={`px-3 py-1 text-xs rounded-full transition-colors flex items-center gap-1 ${goldBias === 'bullish' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200 border border-transparent'}`}
          >
            <TrendingUp size={12} /> Бычий
          </button>
          <button 
            onClick={() => setGoldBias('bearish')}
            className={`px-3 py-1 text-xs rounded-full transition-colors flex items-center gap-1 ${goldBias === 'bearish' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'text-slate-400 hover:text-slate-200 border border-transparent'}`}
          >
            <TrendingDown size={12} /> Медвежий
          </button>
        </div>
      </div>

      {}
      <div className="flex-1 flex flex-col items-center justify-center mb-6 relative min-h-[160px]">
        {/* 3D Claymorphic Sphere */}
        <div className="relative w-40 h-40 flex items-center justify-center">
          {/* Pulsing background rings */}
          <div 
            className={`absolute inset-0 rounded-full animate-ping opacity-20`} 
            style={{ backgroundColor: current.color, animationDuration: '3s' }}
          ></div>
          
          <div 
            className="w-32 h-32 rounded-full relative z-10 transition-all duration-700 ease-in-out"
            style={{
              background: `radial-gradient(circle at 30% 30%, ${current.gradStart}, ${current.color})`,
              boxShadow: `
                inset 10px 10px 20px rgba(255,255,255,0.4), 
                inset -15px -15px 25px rgba(0,0,0,0.6), 
                0 15px 35px ${current.shadowGlow}
              `,
              transform: current.state === 'storm' ? 'scale(1.05)' : 'scale(1)'
            }}
          >
            <div className="absolute inset-0 flex flex-col items-center justify-center text-white/90 drop-shadow-md">
              <IconComponent size={32} className="transition-transform duration-500 hover:scale-110 mb-1" />
              <span className="font-bold tracking-wider text-center text-xs leading-tight px-4">{current.label}</span>
            </div>
          </div>
        </div>
      </div>

      {}
      <div className="space-y-3 mt-auto">
        <div className={`bg-white/5 rounded-xl p-4 border transition-colors duration-500 ${
          current.state === 'storm' 
            ? (goldBias === 'bullish' ? 'border-emerald-500/30 hover:border-emerald-500/50' : 'border-rose-500/30 hover:border-rose-500/50') 
            : 'border-cyan-500/30 hover:border-cyan-500/50'
        }`}>
          <div className="flex justify-between items-start mb-2">
            <div>
              <span className={`font-bold text-lg ${
                current.state === 'storm' 
                  ? (goldBias === 'bullish' ? 'text-emerald-400' : 'text-rose-400') 
                  : 'text-cyan-400'
              }`}>
                {activeAsset}
              </span>
              <div className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                {current.state === 'storm' ? <Zap size={12} /> : <Wind size={12} />} 
                {isQuant ? `Волатильность: ATR ${current.atr}` : current.volatility}
              </div>
            </div>
            
            <div className="flex flex-col items-end gap-1">
              <span className={`px-2 py-1 text-xs font-bold rounded-md border ${
                current.state === 'storm' 
                  ? (goldBias === 'bullish' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border-rose-500/30') 
                  : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
              }`}>
                {current.biasText}
              </span>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider">{current.tag}</span>
            </div>
          </div>
          <p className="text-sm text-slate-300 mt-2 min-h-[40px]">
            {isQuant ? current.descQuant : current.descSimple}
          </p>
        </div>
      </div>
    </GlassCard>
  );
};

const AlgorithmicFleet = ({ isQuant }) => {
  return (
    <GlassCard className="p-6 h-full">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Cpu size={20} className="text-slate-400"/>
          Арена алгоритмов (Флот)
        </h2>
        <span className="text-xs px-2 py-1 bg-white/10 rounded text-slate-300 border border-white/10">5 активных</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {BOTS_DATA.map((bot) => {
          const isActive = bot.status === 'active';
          const isGold = bot.asset.includes('XAU');
          const glowColor = isActive ? (isGold ? 'rgba(16, 185, 129, 0.15)' : 'rgba(6, 182, 212, 0.15)') : 'transparent';
          const borderColor = isActive ? (isGold ? 'border-emerald-500/30' : 'border-cyan-500/30') : 'border-white/5';
          
          return (
            <div 
              key={bot.id} 
              className={`relative overflow-hidden p-4 rounded-xl border ${borderColor} transition-all duration-300`}
              style={{
                backgroundColor: isActive ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.2)',
                boxShadow: isActive ? `0 0 20px ${glowColor}` : 'none',
                opacity: isActive ? 1 : 0.6
              }}
            >
              {/* Bot Header */}
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="text-white font-medium text-sm">{bot.name}</div>
                  <div className={`text-xs ${isGold ? 'text-amber-400' : 'text-cyan-400'}`}>{bot.asset}</div>
                </div>
                {isActive ? (
                  <span className="flex h-3 w-3 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                  </span>
                ) : (
                  <span className="h-2 w-2 rounded-full bg-slate-600"></span>
                )}
              </div>

              {/* Bot Sparkline */}
              <div className="my-3">
                <SparklineChart 
                  data={bot.sparkline} 
                  color={isActive ? (isGold ? COLORS.success : COLORS.silver) : COLORS.textMuted} 
                  isQuant={false} 
                />
              </div>

              {/* Status / Data */}
              <div className="mt-3 pt-3 border-t border-white/10">
                {isQuant ? (
                  <div className="grid grid-cols-3 gap-2 text-xs font-mono text-slate-300">
                    <div>EV: <span className="text-emerald-400">{bot.ev}</span></div>
                    <div>ATR: <span>{bot.atr}</span></div>
                    <div>Win: <span>62%</span></div>
                  </div>
                ) : (
                  <div className="text-xs text-slate-300">
                    {isActive ? (
                      <span className="text-emerald-400">Сценарий: Цель {bot.rTarget}</span>
                    ) : (
                      <span className="text-slate-500">В ожидании фазы...</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </GlassCard>
  );
};

const TimeTravelAIFeed = ({ isQuant }) => {
  const [sliderVal, setSliderVal] = useState(1);
  const currentEvent = TIMELINE_EVENTS[sliderVal];

  return (
    <GlassCard className="p-6 h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Clock size={20} className="text-slate-400"/>
          Машина времени & ИИ Feed
        </h2>
      </div>

      {/* Timeline Slider */}
      <div className="mb-8 bg-white/5 p-4 rounded-xl border border-white/10">
        <input 
          type="range" 
          min="0" 
          max={TIMELINE_EVENTS.length - 1} 
          value={sliderVal} 
          onChange={(e) => setSliderVal(parseInt(e.target.value))}
          className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
        />
        <div className="flex justify-between mt-3 text-xs text-slate-400 font-mono">
          {TIMELINE_EVENTS.map((ev, idx) => (
            <span key={idx} className={sliderVal === idx ? 'text-emerald-400 font-bold scale-110 transition-transform' : ''}>
              {ev.time}
            </span>
          ))}
        </div>
        <div className="mt-3 text-center text-sm text-amber-200">
          <span className="font-bold">{currentEvent.label}</span> — {currentEvent.desc}
        </div>
      </div>

      {/* AI Breakdown Card */}
      <div className="flex-1 bg-black/40 rounded-xl border border-white/10 overflow-hidden flex flex-col">
        {/* Pseudo Chart Snapshot */}
        <div className="h-32 bg-slate-900 relative p-4 flex items-end border-b border-white/10">
          <div className="absolute top-2 right-2 text-[10px] text-slate-500 font-mono">XAU/USD 15m</div>
          {/* Drawing a pseudo candlestick chart layout */}
          <svg className="w-full h-full" viewBox="0 0 100 50" preserveAspectRatio="none">
            {/* FVG Zone */}
            <rect x="20" y="10" width="10" height="20" fill="rgba(244, 63, 94, 0.1)" />
            <text x="22" y="18" fill="rgba(244, 63, 94, 0.5)" fontSize="4" fontFamily="monospace">FVG</text>
            {/* Price line */}
            <path d="M 0,40 L 10,35 L 20,45 L 30,20 L 40,25 L 50,5 L 60,15 L 70,10 L 80,30 L 90,25 L 100,5" fill="none" stroke="#F59E0B" strokeWidth="1.5" />
            {/* AI Highlight */}
            <circle cx="50" cy="5" r="3" fill="none" stroke="#10B981" strokeWidth="1" strokeDasharray="1,1" />
            <line x1="50" y1="5" x2="50" y2="50" stroke="#10B981" strokeWidth="0.5" strokeDasharray="2,2" opacity="0.5" />
          </svg>
        </div>
        
        <div className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2 py-0.5 bg-invalid/20 text-invalid rounded text-[10px] uppercase font-bold border border-invalid/30">
              Закрыто по отмене
            </span>
            <span className="text-xs text-slate-400">15:32 (CPI Release)</span>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">
            {isQuant ? 
              'Вход аннулирован: Скорость тиков превысила 50/сек. Спред расширен до 45 пипсов. Риск удержан в рамках -1.0R (MAE: 12p).' :
              'Сценарий отменен: мощный импульс на выходе новостей сломал зону поддержки. ИИ предотвратил вход. Риск сохранен.'
            }
          </p>
        </div>
      </div>
    </GlassCard>
  );
};

const CommunityIncubator = () => {
  const hypotheses = [
    { id: 1, title: 'Азиатский пробой на Серебре', tested: 82, total: 100 },
    { id: 2, title: 'Реверсия золота в Пятницу', tested: 45, total: 50 },
    { id: 3, title: 'Торговля гепов SPX', tested: 12, total: 30 },
  ];

  return (
    <GlassCard className="p-6 h-full flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Users size={20} className="text-slate-400"/>
            Инкубатор сообщества
          </h2>
          <span className="bg-gradient-to-r from-amber-500 to-amber-300 text-black text-[10px] font-bold px-2 py-1 rounded-full shadow-[0_0_10px_rgba(245,158,11,0.5)]">
            Lifetime Free
          </span>
        </div>

        <div className="space-y-4 mb-6">
          {hypotheses.map(hyp => {
            const percent = (hyp.tested / hyp.total) * 100;
            return (
              <div key={hyp.id} className="bg-white/5 p-3 rounded-lg border border-white/5">
                <div className="flex justify-between text-xs mb-2">
                  <span className="text-slate-200">{hyp.title}</span>
                  <span className="text-slate-400">{hyp.tested}/{hyp.total} дней</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                    style={{ width: `${percent}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <button className="w-full py-3 bg-white/5 hover:bg-white/10 text-white text-sm font-medium rounded-xl border border-white/20 transition-all flex items-center justify-center gap-2 group">
        <Maximize2 size={16} className="text-slate-400 group-hover:text-white transition-colors" />
        Предложить гипотезу
      </button>
    </GlassCard>
  );
};

const AIAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      sender: 'ai', 
      text: 'Привет! Я Ясень 🌳 — нейро-мозг платформы Yasno. Мои алгоритмические "корни" глубоко в рынке, поэтому со мной всё становится ясно. Разберём текущую фазу или логику ботов?',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const messagesEndRef = useRef(null);

  const quickQuestions = [
    "Проясни ситуацию по Золоту",
    "Откуда Бот 1 берёт сигналы?",
    "Что такое R-множитель?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = (text) => {
    const query = text || inputText;
    if (!query.trim()) return;

    // Add user message
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMsg]);
    setInputText('');

    // Mock AI response
    setTimeout(() => {
      const aiMsg = {
        id: Date.now() + 1,
        sender: 'ai',
        text: 'Пропускаю данные через свои нейронные сети... (Демонстрационный ответ). В рабочей версии я покажу вероятности, уровни и объясню всё человеческим языком. С Ясенем всё ясно!',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiMsg]);
    }, 1000);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Chat Window */}
      <div 
        className={`transition-all duration-500 ease-in-out transform origin-bottom-right mb-4 ${
          isOpen ? 'scale-100 opacity-100 translate-y-0' : 'scale-90 opacity-0 translate-y-8 pointer-events-none'
        }`}
      >
        <GlassCard className="w-[340px] sm:w-[400px] h-[500px] flex flex-col shadow-2xl overflow-hidden border-emerald-500/30" glowColor="rgba(16, 185, 129, 0.15)">
          
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/10 bg-gradient-to-r from-emerald-500/10 to-transparent">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="absolute inset-0 bg-emerald-500 rounded-full animate-ping opacity-20"></div>
                <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center relative z-10">
                  <Leaf size={16} className="text-emerald-400" />
                </div>
              </div>
              <div>
                <h3 className="text-white font-medium text-sm flex items-center gap-1.5">
                  Ясень <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono">v1.0</span>
                </h3>
                <p className="text-xs text-emerald-400/80 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_5px_#10B981]"></span> Нейро-аналитик онлайн
                </p>
              </div>
            </div>
            <button 
              onClick={() => setIsOpen(false)}
              className="text-slate-400 hover:text-white transition-colors p-1"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`flex items-end gap-2 max-w-[85%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  
                  {msg.sender === 'ai' && (
                    <div className="w-6 h-6 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center shrink-0 mb-1">
                      <Network size={12} className="text-emerald-300" />
                    </div>
                  )}

                  <div className={`p-3 rounded-2xl text-sm ${
                    msg.sender === 'user' 
                      ? 'bg-emerald-500/20 text-emerald-50 border border-emerald-500/30 rounded-br-sm' 
                      : 'bg-white/5 text-slate-200 border border-white/10 rounded-bl-sm'
                  }`}>
                    {msg.text}
                  </div>
                </div>
                <span className="text-[10px] text-slate-500 mt-1 px-8">{msg.time}</span>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Questions */}
          {messages.length === 1 && (
            <div className="px-4 pb-2 flex flex-wrap gap-2">
              {quickQuestions.map((q, idx) => (
                <button 
                  key={idx}
                  onClick={() => handleSend(q)}
                  className="text-xs bg-white/5 hover:bg-white/10 border border-emerald-500/20 hover:border-emerald-500/40 text-slate-300 hover:text-white rounded-full px-3 py-1.5 transition-all text-left"
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {/* Input Area */}
          <div className="p-4 border-t border-white/10 bg-black/20">
            <form 
              onSubmit={(e) => { e.preventDefault(); handleSend(); }}
              className="relative flex items-center"
            >
              <input 
                type="text" 
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Спроси Ясеня..." 
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-4 pr-12 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 transition-colors"
              />
              <button 
                type="submit"
                disabled={!inputText.trim()}
                className="absolute right-2 p-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 disabled:opacity-50 disabled:hover:bg-emerald-600 transition-all"
              >
                <Send size={16} />
              </button>
            </form>
          </div>
        </GlassCard>
      </div>

      {/* Floating Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`relative group flex items-center justify-center w-14 h-14 rounded-full shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all duration-300 hover:scale-105 ${
          isOpen ? 'bg-slate-800 border border-white/10' : 'bg-gradient-to-tr from-emerald-600 to-teal-500'
        }`}
      >
        <div className="absolute inset-0 rounded-full bg-emerald-400 blur-md opacity-40 group-hover:opacity-60 transition-opacity"></div>
        {isOpen ? (
          <X className="text-white relative z-10" size={24} />
        ) : (
          <Leaf className="text-white relative z-10" size={24} />
        )}
        
        {/* Unread dot simulation */}
        {!isOpen && (
          <span className="absolute top-0 right-0 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500 border-2 border-emerald-600"></span>
          </span>
        )}
      </button>
    </div>
  );
};

const YasnoDashboard = () => {
  const [isQuantMode, setIsQuantMode] = useState(false);

  // Add a subtle background ambient glow
  useEffect(() => {
    document.body.style.backgroundColor = COLORS.bg;
    document.body.style.backgroundImage = 'radial-gradient(circle at 50% -20%, rgba(18, 36, 60, 0.4), #0B0E14)';
    document.body.style.color = COLORS.textMain;
    document.body.style.minHeight = '100vh';
    document.body.style.margin = '0';
    document.body.style.fontFamily = "'Inter', sans-serif";
  }, []);

  return (
    <div className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto selection:bg-emerald-500/30">
      
      {/* Header */}
      <header className="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-700 to-slate-900 border border-white/20 flex items-center justify-center shadow-lg shadow-black/50">
            <Activity className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">Yasno.trade</h1>
            <p className="text-xs text-slate-400 tracking-wider">ЛАБОРАТОРИЯ СТРАТЕГИЙ</p>
          </div>
        </div>

        {/* Global Switcher */}
        <div className="flex items-center bg-black/50 p-1.5 rounded-full border border-white/10 backdrop-blur-md">
          <button 
            onClick={() => setIsQuantMode(false)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${!isQuantMode ? 'bg-white text-black shadow-md' : 'text-slate-400 hover:text-white'}`}
          >
            Просто
          </button>
          <button 
            onClick={() => setIsQuantMode(true)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${isQuantMode ? 'bg-indigo-500 text-white shadow-[0_0_15px_rgba(99,102,241,0.5)]' : 'text-slate-400 hover:text-white'}`}
          >
            Quant / Pro
          </button>
        </div>
      </header>

      {/* Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Row 1: Global Health Bar */}
        <div className="col-span-1 lg:col-span-12">
          <GlobalHealthBar isQuant={isQuantMode} />
        </div>

        {/* Row 2: Radar & Fleet */}
        <div className="col-span-1 lg:col-span-4">
          <MarketRadar isQuant={isQuantMode} />
        </div>
        <div className="col-span-1 lg:col-span-8">
          <AlgorithmicFleet isQuant={isQuantMode} />
        </div>

        {/* Row 3: Time Travel & Community */}
        <div className="col-span-1 lg:col-span-7">
          <TimeTravelAIFeed isQuant={isQuantMode} />
        </div>
        <div className="col-span-1 lg:col-span-5">
          <CommunityIncubator />
        </div>

      </div>

      {/* Floating AI Assistant */}
      <AIAssistant />
    </div>
  );
};

export default YasnoDashboard;