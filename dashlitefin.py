<!DOCTYPE html>
<html lang="ru" class="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yasno.trade | Лаборатория рыночных стратегий</title>
    
    <!-- Подключение Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Подключение шрифта Inter -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <!-- Подключение иконок Phosphor -->
    <script src="https://unpkg.com/@phosphor-icons/web"></script>

    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                    },
                    colors: {
                        brand: {
                            bg: '#F8FAFC',
                            'bg-dark': '#090D16',
                            card: 'rgba(255, 255, 255, 0.75)',
                            'card-dark': 'rgba(15, 23, 42, 0.75)',
                            border: 'rgba(226, 232, 240, 0.8)',
                            'border-dark': 'rgba(255, 255, 255, 0.08)',
                        },
                        emerald: { 
                            400: '#34D399', 
                            500: '#10B981', 
                            600: '#059669',
                            50: '#ECFDF5',
                            900: 'rgba(16, 185, 129, 0.12)' 
                        },
                        coral: { 
                            500: '#F43F5E', 
                            50: '#FFF1F2',
                            900: 'rgba(244, 63, 94, 0.12)' 
                        },
                        amber: { 
                            500: '#F59E0B', 
                            50: '#FFFBEB',
                            900: 'rgba(245, 158, 11, 0.12)' 
                        },
                        cyan: { 
                            500: '#06B6D4', 
                            600: '#0891B2',
                            50: '#ECFEFF',
                            900: 'rgba(6, 182, 212, 0.12)' 
                        },
                    },
                    boxShadow: {
                        'glass': '0 20px 40px -15px rgba(15, 23, 42, 0.05), 0 0 15px 0 rgba(255, 255, 255, 0.5) inset',
                        'glass-hover': '0 25px 50px -12px rgba(15, 23, 42, 0.09), 0 0 20px 0 rgba(255, 255, 255, 0.8) inset',
                        'glow-emerald': '0 10px 30px -5px rgba(16, 185, 129, 0.25)',
                    }
                }
            }
        }
    </script>

    <style>
        /* Базовые стили фоновой 'ауры' с воздушными светящимися пятнами */
        body {
            font-family: 'Inter', sans-serif;
            transition: background-color 0.4s ease, color 0.4s ease;
        }

        /* Фоновые градиентные пятна для эффекта объема и света */
        .aurora-bg {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -1;
            overflow: hidden;
            pointer-events: none;
        }

        .aurora-blob {
            position: absolute;
            border-radius: 50%;
            filter: blur(90px);
            opacity: 0.6;
            animation: float 18s infinite alternate ease-in-out;
        }

        .dark .aurora-blob {
            opacity: 0.25;
        }

        @keyframes float {
            0% { transform: translate(0px, 0px) scale(1); }
            50% { transform: translate(40px, -30px) scale(1.08); }
            100% { transform: translate(-30px, 20px) scale(0.95); }
        }

        /* Стекло из матовой прозрачной эмали */
        .glass-panel {
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(226, 232, 240, 0.9);
            box-shadow: 0 10px 30px -10px rgba(15, 23, 42, 0.04), 0 1px 2px 0 rgba(0, 0, 0, 0.02);
            border-radius: 1.25rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .dark .glass-panel {
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        }

        .glass-panel-hover:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 35px -12px rgba(15, 23, 42, 0.08);
        }

        .dark .glass-panel-hover:hover {
            box-shadow: 0 20px 35px -12px rgba(0, 0, 0, 0.6);
        }

        /* Неоновое выделение фокусного бота */
        .glow-active {
            border-color: rgba(16, 185, 129, 0.6) !important;
            box-shadow: 0 0 25px rgba(16, 185, 129, 0.18), 0 10px 25px -5px rgba(16, 185, 129, 0.1) !important;
        }

        /* Кастомный аккуратный скроллбар */
        .custom-scrollbar::-webkit-scrollbar {
            width: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: rgba(148, 163, 184, 0.3);
            border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: rgba(148, 163, 184, 0.5);
        }

        /* Анимация появления элементов */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message-anim {
            animation: fadeInUp 0.25s ease-out forwards;
        }

        /* --- НОВЫЕ СТИЛИ ДЛЯ УЛУЧШЕНИЙ --- */
        .bot-card { cursor: pointer; }
        .bot-details { 
            display: grid;
            grid-template-rows: 0fr;
            transition: grid-template-rows 0.3s ease-out;
        }
        .bot-details.open {
            grid-template-rows: 1fr;
        }
        .bot-details-inner { overflow: hidden; }
        
        .ai-toast {
            animation: slideInDown 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        @keyframes slideInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .gauge-circle {
            transition: stroke-dashoffset 1s ease-out;
        }
        
        @keyframes shimmer {
            100% { transform: translateX(100%); }
        }
    </style>
</head>
<body class="bg-brand-bg dark:bg-brand-bg-dark text-slate-800 dark:text-slate-100 min-h-screen p-4 sm:p-6 lg:p-8 flex flex-col items-center selection:bg-cyan-500 selection:text-white">

    <!-- Динамический светящийся фон для ощущения воздуха и объемного света -->
    <div class="aurora-bg">
        <div class="aurora-blob bg-cyan-200 dark:bg-cyan-900/40 w-[500px] h-[500px] -top-32 -left-32"></div>
        <div class="aurora-blob bg-emerald-200 dark:bg-emerald-900/30 w-[600px] h-[600px] top-1/3 -right-40" style="animation-delay: -6s;"></div>
        <div class="aurora-blob bg-indigo-200 dark:bg-indigo-900/30 w-[450px] h-[450px] -bottom-20 left-1/4" style="animation-delay: -12s;"></div>
    </div>

    <!-- Основной контейнер платформы -->
    <div class="w-full max-w-6xl flex flex-col gap-6">
        
            <!-- HEADER MODULE -->
        <header class="glass-panel px-6 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-3.5">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 via-emerald-400 to-emerald-500 flex items-center justify-center shadow-md shadow-cyan-500/20 text-white">
                    <i class="ph-bold ph-chart-line-up text-xl"></i>
                </div>
                <div>
                    <h1 class="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                        Yasno.trade
                    </h1>
                    <p class="text-xs font-medium text-slate-500 dark:text-slate-400">Лаборатория рыночных стратегий</p>
                </div>
            </div>
            
            <div class="flex items-center gap-3 sm:gap-4 text-xs sm:text-sm font-semibold">
                <!-- Статус активности -->
                <div class="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-500/30 text-emerald-700 dark:text-emerald-400">
                    <span class="relative flex h-2 w-2">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span>Live Status: Активен</span>
                </div>

                <!-- Кнопка переключения темы Light / Dark -->
                <button onclick="toggleTheme()" id="theme-toggle" title="Сменить тему оформления" 
                        class="p-2 rounded-xl bg-slate-200/60 dark:bg-slate-800/80 hover:bg-slate-300/60 dark:hover:bg-slate-700 text-slate-700 dark:text-amber-400 transition-colors border border-slate-300/40 dark:border-white/10 flex items-center justify-center">
                    <i id="theme-icon" class="ph-bold ph-sun text-lg"></i>
                </button>
            </div>
        </header>

        <!-- TOP METRICS (Hero Bar) -->
        <section class="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6">
            <!-- Совокупный R-профит -->
            <div class="glass-panel p-5 flex flex-col justify-between relative group h-full gap-4 hover:z-50 transition-all duration-300">
                <!-- Изолированный слой для фонового свечения, чтобы не обрезать Tooltip -->
                <div class="absolute inset-0 overflow-hidden rounded-[1.25rem] pointer-events-none">
                    <div class="absolute -right-6 -top-6 w-24 h-24 bg-emerald-400/10 rounded-full blur-xl group-hover:scale-150 transition-transform"></div>
                </div>
                
                <div class="flex flex-wrap sm:flex-nowrap justify-between items-start w-full z-10 gap-3 sm:gap-2">
                    <span class="text-xs font-bold text-slate-400 dark:text-slate-400 uppercase tracking-wider min-w-[120px]">Суммарный профит</span>
                    <!-- Переключатель периодов -->
                    <div class="flex bg-slate-200/50 dark:bg-slate-800/50 rounded-lg p-0.5 border border-slate-300/40 dark:border-white/5 text-[10px] font-semibold flex-shrink-0 w-full sm:w-auto">
                        <button onclick="setPeriod(this, 'all', 148.5)" class="px-2 py-1 rounded-md bg-white dark:bg-slate-700 text-slate-800 dark:text-white shadow-sm transition-all period-btn active-period flex-1 sm:flex-none">Всё время</button>
                        <button onclick="setPeriod(this, 'month', 84.2)" class="px-2 py-1 rounded-md text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-all period-btn flex-1 sm:flex-none">Месяц</button>
                        <button onclick="setPeriod(this, 'week', 21.4)" class="px-2 py-1 rounded-md text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-all period-btn flex-1 sm:flex-none">Неделя</button>
                    </div>
                </div>

                <div class="flex items-end justify-between w-full z-10">
                    <div class="flex flex-col relative">
                        <div class="group/tooltip flex flex-col w-fit relative cursor-help z-50">
                            <span id="total-profit-val" class="text-2xl sm:text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 tracking-tight transition-all duration-300 border-b border-dashed border-emerald-500/50 pb-0.5 whitespace-nowrap">+148.5 R</span>
                            
                            <!-- Всплывающая подсказка (Tooltip) -->
                            <div class="absolute top-full left-0 mt-3 w-[calc(100vw-3rem)] max-w-[280px] sm:max-w-[320px] p-3.5 bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl border border-slate-200 dark:border-white/10 rounded-xl shadow-2xl opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all duration-200 text-[11px] sm:text-xs leading-relaxed text-slate-600 dark:text-slate-300 pointer-events-none translate-y-2 group-hover/tooltip:translate-y-0 z-[100]">
                                Показатель отражает чистый результат работы алгоритмов: сумму всех прибыльных отработок за вычетом тех сценариев, которые ушли в минус. Мы считаем результат в R, а не в деньгах, чтобы объективно показать математику стратегий независимо от размера вашего депозита.
                            </div>
                        </div>
                        <span class="text-[11px] font-medium text-emerald-700/70 dark:text-emerald-400/70 mt-1.5 flex items-center gap-1 whitespace-nowrap">
                            <i class="ph-bold ph-trend-up"></i> Высокий темп прироста
                        </span>
                    </div>
                    <!-- Sparkline (Мини-график) -->
                    <div class="w-16 sm:w-20 h-10 ml-2 relative opacity-80 flex-shrink-0">
                        <svg viewBox="0 0 100 30" class="w-full h-full stroke-emerald-500 fill-none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M5,25 Q15,20 25,22 T45,15 T65,18 T85,5 L95,2" />
                            <path d="M5,25 Q15,20 25,22 T45,15 T65,18 T85,5 L95,2 L95,30 L5,30 Z" class="fill-emerald-500/10 stroke-none" />
                        </svg>
                    </div>
                </div>
            </div>

            <!-- Индекс реализации -->
            <div class="glass-panel p-5 flex flex-col justify-between relative group h-full gap-4 hover:z-50 transition-all duration-300">
                <div class="absolute inset-0 overflow-hidden rounded-[1.25rem] pointer-events-none">
                    <div class="absolute -right-6 -top-6 w-24 h-24 bg-cyan-400/10 rounded-full blur-xl group-hover:scale-150 transition-transform"></div>
                </div>
                
                <div class="flex justify-between items-start w-full z-10">
                    <span class="text-xs font-bold text-slate-400 dark:text-slate-400 uppercase tracking-wider">Индекс реализации</span>
                    <div class="w-7 h-7 rounded-lg bg-cyan-50 dark:bg-cyan-900/30 text-cyan-500 dark:text-cyan-400 flex items-center justify-center flex-shrink-0 shadow-sm border border-cyan-100 dark:border-cyan-500/20">
                        <i class="ph-bold ph-target"></i>
                    </div>
                </div>

                <div class="flex items-end justify-between w-full z-10">
                    <div class="flex flex-col relative">
                        <span class="text-2xl sm:text-3xl font-extrabold text-slate-800 dark:text-white tracking-tight whitespace-nowrap">69.4%</span>
                        <span class="text-[11px] font-medium text-slate-500 dark:text-slate-400 mt-1.5 flex items-center gap-1 whitespace-nowrap">
                            Точность сигналов
                        </span>
                    </div>
                    <!-- Mini Gauge -->
                    <div class="w-10 h-10 ml-2 relative opacity-90 flex-shrink-0 drop-shadow-sm">
                        <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                            <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="currentColor" stroke-width="4" class="text-slate-200 dark:text-slate-700/50"></circle>
                            <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="currentColor" stroke-width="4" stroke-dasharray="69.4, 100" stroke-linecap="round" class="text-cyan-500"></circle>
                        </svg>
                    </div>
                </div>
            </div>

            <!-- Активные агенты -->
            <div class="glass-panel p-5 flex flex-col justify-between relative group h-full gap-4 hover:z-50 transition-all duration-300">
                <div class="absolute inset-0 overflow-hidden rounded-[1.25rem] pointer-events-none">
                    <div class="absolute -right-6 -top-6 w-24 h-24 bg-indigo-400/10 rounded-full blur-xl group-hover:scale-150 transition-transform"></div>
                </div>
                
                <div class="flex justify-between items-start w-full z-10">
                    <span class="text-xs font-bold text-slate-400 dark:text-slate-400 uppercase tracking-wider">Активные агенты</span>
                    <div class="w-7 h-7 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 text-indigo-500 dark:text-indigo-400 flex items-center justify-center flex-shrink-0 shadow-sm border border-indigo-100 dark:border-indigo-500/20">
                        <i class="ph-bold ph-cpu"></i>
                    </div>
                </div>

                <div class="flex items-end justify-between w-full z-10">
                    <div class="flex flex-col relative">
                        <span class="text-2xl sm:text-3xl font-extrabold text-slate-800 dark:text-white tracking-tight flex items-baseline gap-1.5 whitespace-nowrap">
                            5 <span class="text-sm font-semibold text-slate-400 dark:text-slate-500">/ 12</span>
                        </span>
                        <span class="text-[11px] font-medium text-emerald-600 dark:text-emerald-400 mt-1.5 flex items-center gap-1.5 whitespace-nowrap">
                            <span class="relative flex h-2 w-2">
                                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                            </span>
                            Системы онлайн
                        </span>
                    </div>
                    <!-- Иконки ботов -->
                    <div class="flex -space-x-2 overflow-hidden items-center ml-2 p-1">
                        <div class="inline-flex h-7 w-7 items-center justify-center rounded-full ring-2 ring-white dark:ring-[#1a202c] bg-emerald-500 shadow-sm z-30">
                            <i class="ph-bold ph-robot text-white text-[10px]"></i>
                        </div>
                        <div class="inline-flex h-7 w-7 items-center justify-center rounded-full ring-2 ring-white dark:ring-[#1a202c] bg-cyan-500 shadow-sm z-20">
                            <i class="ph-bold ph-robot text-white text-[10px]"></i>
                        </div>
                        <div class="inline-flex h-7 w-7 items-center justify-center rounded-full ring-2 ring-white dark:ring-[#1a202c] bg-amber-500 shadow-sm z-10">
                            <i class="ph-bold ph-robot text-white text-[10px]"></i>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- MAIN SECTION: MARKET WEATHER & BOT ARENA -->
        <section class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            <!-- МОДУЛЬ 2. ПОГОДА РЫНКА (Market Weather) -->
            <div class="lg:col-span-5 glass-panel p-6 flex flex-col gap-5">
                <div class="flex items-center justify-between border-b border-slate-200/80 dark:border-white/10 pb-3.5">
                    <div class="flex items-center gap-2.5">
                        <div class="w-8 h-8 rounded-lg bg-amber-500/10 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400 flex items-center justify-center">
                            <i class="ph-bold ph-sun-dim text-lg"></i>
                        </div>
                        <h2 class="text-lg font-bold text-slate-900 dark:text-white">Погода рынка</h2>
                    </div>
                    <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
                        Обновлено 2м назад
                    </span>
                </div>
                
                <div class="flex flex-col gap-4">
                    <!-- Карточка Золота (XAU/USD) -->
                <div class="glass-panel p-4 border border-emerald-200/80 dark:border-emerald-500/30 bg-emerald-50/40 dark:bg-emerald-900/10 rounded-2xl relative overflow-hidden group transition-all">
                    <div class="flex justify-between items-start mb-3">
                        <div>
                            <span class="text-xs font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider">XAU / USD</span>
                            <h3 class="font-bold text-base text-slate-900 dark:text-white">Золото</h3>
                        </div>
                        <span class="inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-lg bg-emerald-500 text-white shadow-sm shadow-emerald-500/30">
                            <i class="ph-bold ph-lightning"></i> Бычий шторм
                        </span>
                    </div>
                    <div class="flex items-center gap-4">
                        <!-- Gauge Indicator (Радар погоды) -->
                        <div class="relative w-14 h-14 flex-shrink-0">
                            <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="currentColor" stroke-width="3" class="text-emerald-200 dark:text-emerald-900/50"></circle>
                                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="currentColor" stroke-width="3" stroke-dasharray="92, 100" stroke-linecap="round" class="text-emerald-500 gauge-circle"></circle>
                            </svg>
                            <div class="absolute inset-0 flex flex-col items-center justify-center">
                                <span class="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 leading-none">92%</span>
                            </div>
                        </div>
                        <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 font-medium leading-relaxed">
                            Мощный восходящий импульс. В приоритете трендовые модели на покупку на локальных откатах.
                        </p>
                    </div>
                </div>

                <!-- Карточка Серебра (XAG/USD) -->
                <div class="glass-panel p-4 border border-cyan-200/80 dark:border-cyan-500/30 bg-cyan-50/40 dark:bg-cyan-900/10 rounded-2xl relative overflow-hidden group transition-all">
                    <div class="flex justify-between items-start mb-3">
                        <div>
                            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">XAG / USD</span>
                            <h3 class="font-bold text-base text-slate-900 dark:text-white">Серебро</h3>
                        </div>
                        <span class="inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-lg bg-cyan-500 text-white shadow-sm shadow-cyan-500/30">
                            <i class="ph-bold ph-waves"></i> Штиль
                        </span>
                    </div>
                    <div class="flex items-center gap-4">
                        <!-- Gauge Indicator (Радар погоды) -->
                        <div class="relative w-14 h-14 flex-shrink-0">
                            <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="currentColor" stroke-width="3" class="text-cyan-200 dark:text-cyan-900/50"></circle>
                                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="currentColor" stroke-width="3" stroke-dasharray="15, 100" stroke-linecap="round" class="text-cyan-500 gauge-circle"></circle>
                            </svg>
                            <div class="absolute inset-0 flex flex-col items-center justify-center">
                                <span class="text-[10px] font-bold text-cyan-700 dark:text-cyan-400 leading-none">15%</span>
                            </div>
                        </div>
                        <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 font-medium leading-relaxed">
                            Узкий боковой диапазон. Активированы алгоритмы работы от границ коридора (Mean Reversion).
                        </p>
                    </div>
                </div>
            </div>

            <!-- Глобальный фокус -->
                <div class="mt-auto pt-4 bg-emerald-50 dark:bg-emerald-950/30 rounded-xl p-3.5 border border-emerald-200/80 dark:border-emerald-500/20 flex items-start gap-3">
                    <div class="p-2 rounded-lg bg-emerald-500 text-white flex-shrink-0 mt-0.5 shadow-sm">
                        <i class="ph-bold ph-target text-base"></i>
                    </div>
                    <div>
                        <span class="block text-xs font-bold text-emerald-800 dark:text-emerald-400 uppercase tracking-wider mb-0.5">Глобальный фокус дня</span>
                        <span class="text-xs font-semibold text-slate-700 dark:text-slate-200">Лонг-сетапы на откате (Pullback) в мажоритарных драгметаллах.</span>
                    </div>
                </div>
            </div>

            <!-- МОДУЛЬ 3. АРЕНА БОТОВ (Algorithmic Grid) -->
            <div class="lg:col-span-7 glass-panel p-6 flex flex-col gap-5">
                <div class="flex items-center justify-between border-b border-slate-200/80 dark:border-white/10 pb-3.5">
                    <div class="flex items-center gap-2.5">
                        <div class="w-8 h-8 rounded-lg bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 flex items-center justify-center">
                            <i class="ph-bold ph-robot text-lg"></i>
                        </div>
                        <h2 class="text-lg font-bold text-slate-900 dark:text-white">Арена ботов</h2>
                    </div>
                    <span class="text-xs font-semibold text-slate-400 dark:text-slate-400">Top Performers</span>
                </div>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <!-- Бот 1 (Активный - Подсвечен) -->
                <div class="glass-panel p-4 text-slate-800 dark:text-white glow-active relative flex flex-col gap-3 glass-panel-hover bg-white/90 dark:bg-slate-800/90 bot-card" onclick="toggleBotDetails('bot1')">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="font-bold text-base text-slate-900 dark:text-white flex items-center gap-1.5">
                                Бот #1 
                            </h3>
                            <span class="text-xs font-medium text-slate-500 dark:text-slate-400">Impulse Pullback</span>
                        </div>
                        <span class="text-[11px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-500 text-white shadow-sm">
                            Live
                        </span>
                    </div>
                    <div class="flex justify-between items-end">
                        <div class="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 tracking-tight">+42.0 R</div>
                        <!-- Mini Sparkline (Микро-график) -->
                        <div class="w-16 h-8 opacity-80 mb-1">
                            <svg viewBox="0 0 100 30" class="w-full h-full stroke-emerald-500 fill-none" stroke-width="3" stroke-linecap="round">
                                <path d="M0,25 L20,20 L40,25 L60,10 L80,15 L100,5" />
                            </svg>
                        </div>
                    </div>
                    <div class="text-xs font-medium text-emerald-700 dark:text-emerald-400 flex items-center justify-between pt-2 border-t border-slate-100 dark:border-white/5">
                        <span class="flex items-center gap-1.5"><i class="ph-bold ph-check-circle text-base"></i> Идеально совпадает с «Штормом»</span>
                        <i class="ph-bold ph-caret-down text-emerald-500 transition-transform" id="bot1-icon"></i>
                    </div>
                    
                    <!-- Drill-down Details (Скрытая панель) -->
                    <div id="bot1-details" class="bot-details">
                        <div class="bot-details-inner flex flex-col gap-2 pt-3">
                            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Последние сделки</div>
                            <div class="flex justify-between items-center bg-slate-50 dark:bg-slate-800/50 p-2 rounded-lg border border-slate-100 dark:border-white/5">
                                <div class="flex items-center gap-2">
                                    <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                                    <span class="text-xs font-medium text-slate-700 dark:text-slate-300">XAU/USD Long</span>
                                </div>
                                <span class="text-xs font-bold text-emerald-600 dark:text-emerald-400">+3.5 R</span>
                            </div>
                            <div class="flex justify-between items-center bg-slate-50 dark:bg-slate-800/50 p-2 rounded-lg border border-slate-100 dark:border-white/5">
                                <div class="flex items-center gap-2">
                                    <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                                    <span class="text-xs font-medium text-slate-700 dark:text-slate-300">XAU/USD Long</span>
                                </div>
                                <span class="text-xs font-bold text-emerald-600 dark:text-emerald-400">+4.2 R</span>
                            </div>
                            <div class="mt-1 bg-amber-50 dark:bg-amber-900/20 p-2 rounded-lg border border-amber-200/50 dark:border-amber-500/20 flex justify-between items-center">
                                <span class="text-[11px] font-semibold text-amber-700 dark:text-amber-400 flex items-center gap-1.5"><i class="ph-bold ph-target"></i> Открыт ордер (Trailing)</span>
                                <span class="text-xs font-bold text-amber-600 dark:text-amber-400">+1.2 R</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Бот 2 (Ожидание) -->
                <div class="glass-panel p-4 text-slate-800 dark:text-white flex flex-col gap-3 glass-panel-hover bot-card" onclick="toggleBotDetails('bot2')">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="font-bold text-base text-slate-900 dark:text-white">Бот #2</h3>
                            <span class="text-xs font-medium text-slate-500 dark:text-slate-400">RSI Divergence</span>
                        </div>
                        <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400 border border-amber-300/60 dark:border-amber-500/30">
                            Ожидание
                        </span>
                    </div>
                    <div class="flex justify-between items-end">
                        <div class="text-3xl font-extrabold text-slate-800 dark:text-white tracking-tight">+18.5 R</div>
                        <!-- Mini Sparkline Flat -->
                        <div class="w-16 h-8 opacity-40 mb-1">
                            <svg viewBox="0 0 100 30" class="w-full h-full stroke-slate-500 fill-none" stroke-width="2" stroke-linecap="round">
                                <path d="M0,15 L100,15" stroke-dasharray="4,4" />
                            </svg>
                        </div>
                    </div>
                    <div class="text-xs font-medium text-amber-700 dark:text-amber-400 flex items-center justify-between pt-2 border-t border-slate-100 dark:border-white/5">
                        <span class="flex items-center gap-1.5"><i class="ph-bold ph-hourglass-high text-base"></i> Ждет смены фазы</span>
                        <i class="ph-bold ph-caret-down text-slate-400 transition-transform" id="bot2-icon"></i>
                    </div>
                    <!-- Drill-down Details -->
                    <div id="bot2-details" class="bot-details">
                        <div class="bot-details-inner flex flex-col gap-2 pt-3">
                            <div class="text-[11px] text-center text-slate-500 dark:text-slate-400 italic">Нет активных позиций. Последняя сделка закрыта 4ч назад.</div>
                        </div>
                    </div>
                </div>

                <!-- Бот 3 (Активен) -->
                <div class="glass-panel p-4 text-slate-800 dark:text-white flex flex-col gap-3 glass-panel-hover bot-card" onclick="toggleBotDetails('bot3')">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="font-bold text-base text-slate-900 dark:text-white">Бот #3</h3>
                            <span class="text-xs font-medium text-slate-500 dark:text-slate-400">Structure Break</span>
                        </div>
                        <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-cyan-100 dark:bg-cyan-900/40 text-cyan-700 dark:text-cyan-300 border border-cyan-300/60 dark:border-cyan-500/30">
                            Активен
                        </span>
                    </div>
                    <div class="flex justify-between items-end">
                        <div class="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 tracking-tight">+31.2 R</div>
                        <!-- Mini Sparkline -->
                        <div class="w-16 h-8 opacity-80 mb-1">
                            <svg viewBox="0 0 100 30" class="w-full h-full stroke-cyan-500 fill-none" stroke-width="3" stroke-linecap="round">
                                <path d="M0,20 L30,22 L50,15 L70,18 L100,5" />
                            </svg>
                        </div>
                    </div>
                    <div class="text-xs font-medium text-slate-500 dark:text-slate-400 flex items-center justify-between pt-2 border-t border-slate-100 dark:border-white/5">
                        <span class="flex items-center gap-1.5"><i class="ph-bold ph-activity text-base text-cyan-500"></i> Сканирует пробой M15</span>
                        <i class="ph-bold ph-caret-down text-slate-400 transition-transform" id="bot3-icon"></i>
                    </div>
                    <!-- Drill-down Details -->
                    <div id="bot3-details" class="bot-details">
                        <div class="bot-details-inner flex flex-col gap-2 pt-3">
                            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Сенсоры (Live)</div>
                            <div class="flex justify-between items-center bg-slate-50 dark:bg-slate-800/50 p-2 rounded-lg border border-slate-100 dark:border-white/5">
                                <span class="text-xs font-medium text-slate-700 dark:text-slate-300">Уровень сопротивления</span>
                                <span class="text-xs font-bold text-slate-900 dark:text-white">2,345.10</span>
                            </div>
                            <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-1 mt-1">
                                <div class="bg-cyan-500 h-1 rounded-full animate-pulse" style="width: 85%"></div>
                            </div>
                            <div class="text-[10px] text-right text-slate-500">Приближение к зоне: 85%</div>
                        </div>
                    </div>
                </div>

                <!-- Бот 4 (Спящий режим) -->
                <div class="glass-panel p-4 opacity-60 dark:opacity-50 flex flex-col gap-3 hover:opacity-100 transition-opacity">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="font-bold text-base text-slate-700 dark:text-slate-300">Бот #4</h3>
                            <span class="text-xs font-medium text-slate-400">Mean Reversion</span>
                        </div>
                        <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
                            Standby
                        </span>
                    </div>
                    <div class="text-3xl font-extrabold text-slate-500 dark:text-slate-400 tracking-tight">+12.4 R</div>
                    <div class="text-xs font-medium text-slate-400 flex items-center gap-1.5 pt-2 border-t border-slate-100 dark:border-white/5">
                        <i class="ph-bold ph-moon-stars text-base"></i> Отключен во время «Шторма»
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- МОДУЛЬ 4. ВСТРОЕННЫЙ ИИ-ПОМОЩНИК (AI Strategy Assistant) -->
        <section class="glass-panel flex flex-col overflow-hidden border-t-2 border-t-cyan-500">
            <!-- Шапка чата -->
            <div class="bg-cyan-500/5 dark:bg-cyan-900/20 px-6 py-4 flex items-center justify-between border-b border-slate-200/80 dark:border-white/5">
                <div class="flex items-center gap-3.5">
                    <div class="w-10 h-10 rounded-xl bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 flex items-center justify-center relative shadow-sm">
                        <i class="ph-bold ph-sparkle text-xl"></i>
                        <span class="absolute top-0 right-0 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white dark:border-slate-900"></span>
                    </div>
                    <div>
                        <h3 class="font-bold text-slate-900 dark:text-white text-base">AI Strategy Assistant</h3>
                        <p class="text-xs font-medium text-slate-500 dark:text-cyan-400/80">Пояснит погоду рынка и логику работы алгоритмов в реальном времени</p>
                    </div>
                </div>
                <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-cyan-100 dark:bg-cyan-950 text-cyan-700 dark:text-cyan-300 hidden sm:inline-block">
                    Gemini 3.1 Powered
                </span>
            </div>

            <!-- Диалоговое окно сообщений -->
        <div id="chat-messages" class="relative p-6 flex flex-col gap-4 h-72 overflow-y-auto custom-scrollbar bg-slate-50/50 dark:bg-slate-950/20">
            
            <!-- Proactive AI Toast (Push-инсайт) -->
            <div id="proactive-toast" class="hidden absolute top-4 left-6 right-6 z-10 ai-toast">
                <div class="bg-white/95 dark:bg-slate-800/95 border border-cyan-200/80 dark:border-cyan-500/30 rounded-xl p-3 shadow-lg shadow-cyan-500/10 flex items-start gap-3 backdrop-blur-md">
                    <div class="w-6 h-6 rounded-full bg-cyan-500 text-white flex-shrink-0 flex items-center justify-center mt-0.5 shadow-sm shadow-cyan-500/30">
                        <i class="ph-bold ph-bell-ringing text-xs"></i>
                    </div>
                    <div class="flex-1">
                        <span class="text-[10px] font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-wider mb-0.5 block">Live-Инсайт (Событие)</span>
                        <p class="text-[13px] font-medium text-slate-700 dark:text-slate-200 leading-tight">
                            Сенсоры фиксируют падение волатильности на XAG/USD. Алгоритм Бота #4 переведен в режим сканирования границ.
                        </p>
                    </div>
                    <button onclick="document.getElementById('proactive-toast').style.display='none'" class="ml-1 text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300">
                        <i class="ph-bold ph-x text-sm"></i>
                    </button>
                </div>
            </div>

            <!-- Сообщение от ИИ -->
            <div class="flex gap-3 max-w-[85%] mt-2">
                </button>
            </div>
        </div>

        <!-- Поле ввода вопроса с быстрыми подсказками -->
        <div class="p-4 bg-white/80 dark:bg-slate-900/80 border-t border-slate-200/80 dark:border-white/10 flex flex-col gap-3">
            
            <!-- Чипы быстрых вопросов -->
            <div class="flex flex-wrap gap-2">
                <button onclick="sendPrompt('Что с золотом?')" class="px-3 py-1.5 rounded-full bg-cyan-50/80 hover:bg-cyan-100 dark:bg-cyan-900/30 dark:hover:bg-cyan-800/50 border border-cyan-200/60 dark:border-cyan-700/30 text-[11px] sm:text-xs font-semibold text-cyan-700 dark:text-cyan-300 transition-all shadow-sm hover:shadow hover:-translate-y-0.5 whitespace-nowrap">
                    Что с золотом?
                </button>
                <button onclick="sendPrompt('Почему сработал бот 1?')" class="px-3 py-1.5 rounded-full bg-cyan-50/80 hover:bg-cyan-100 dark:bg-cyan-900/30 dark:hover:bg-cyan-800/50 border border-cyan-200/60 dark:border-cyan-700/30 text-[11px] sm:text-xs font-semibold text-cyan-700 dark:text-cyan-300 transition-all shadow-sm hover:shadow hover:-translate-y-0.5 whitespace-nowrap">
                    Почему сработал Бот #1?
                </button>
                <button onclick="sendPrompt('Объясни последний сбой')" class="px-3 py-1.5 rounded-full bg-cyan-50/80 hover:bg-cyan-100 dark:bg-cyan-900/30 dark:hover:bg-cyan-800/50 border border-cyan-200/60 dark:border-cyan-700/30 text-[11px] sm:text-xs font-semibold text-cyan-700 dark:text-cyan-300 transition-all shadow-sm hover:shadow hover:-translate-y-0.5 whitespace-nowrap">
                    Объясни последний сбой
                </button>
            </div>

            <div class="relative flex items-center">
                <input type="text" id="chat-input" placeholder="Спросите ассистента о погоде или ботах..." 
                       class="w-full bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-white/10 rounded-xl py-3 pl-4 pr-12 text-xs sm:text-sm font-medium text-slate-800 dark:text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition-colors"
                       onkeypress="handleKeyPress(event)">
                <button onclick="handleSend()" class="absolute right-2 p-2 rounded-lg bg-cyan-500 hover:bg-cyan-600 text-white flex items-center justify-center transition-colors shadow-md shadow-cyan-500/20">
                    <i class="ph-bold ph-paper-plane-right text-base"></i>
                </button>
            </div>
        </div>
    </section>

    <!-- FOOTER: ИНКУБАТОР ГИПОТЕЗ -->
    <footer class="mt-2 mb-8 flex flex-col items-center gap-5 text-center w-full">
        
        <!-- Геймификация / Social Proof -->
        <div class="glass-panel px-6 py-4 rounded-2xl w-full max-w-md flex flex-col gap-2.5 relative overflow-hidden group">
            <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/0 via-emerald-500/10 to-emerald-500/0 translate-x-[-100%] animate-[shimmer_4s_infinite]"></div>
            
            <div class="flex justify-between items-center text-xs font-bold z-10">
                <span class="text-slate-600 dark:text-slate-300">Проверено гипотез за сегодня: <span class="text-emerald-600 dark:text-emerald-400">12</span></span>
                <span class="text-amber-500 flex items-center gap-1 bg-amber-50 dark:bg-amber-900/20 px-2 py-0.5 rounded-md border border-amber-200 dark:border-amber-500/20"><i class="ph-fill ph-fire"></i> Hot</span>
            </div>
            
            <!-- Progress bar -->
            <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden z-10">
                <div class="bg-gradient-to-r from-cyan-400 to-emerald-500 h-2 rounded-full relative" style="width: 78%">
                    <div class="absolute inset-0 bg-white/20 animate-pulse"></div>
                </div>
            </div>
            
            <div class="text-[11px] text-slate-500 dark:text-slate-400 font-medium z-10 mt-0.5">
                Пользователь <span class="font-bold text-slate-700 dark:text-slate-200">@Alex_Q</span> только что получил статус <span class="text-emerald-600 dark:text-emerald-400">Founding Member</span> 🎉
            </div>
        </div>

        <button class="group relative px-6 py-3.5 bg-white dark:bg-slate-800 border border-slate-200/90 dark:border-white/10 rounded-2xl flex items-center gap-2.5 hover:border-emerald-500 shadow-lg shadow-slate-200/50 dark:shadow-none transition-all overflow-hidden z-10">
            <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/0 via-emerald-500/10 to-emerald-500/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
            <div class="w-7 h-7 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">
                <i class="ph-bold ph-lightbulb text-lg"></i>
            </div>
            <span class="font-bold text-sm text-slate-800 dark:text-white">+ Предложить свою гипотезу</span>
        </button>
        
        <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center justify-center gap-1.5 z-10">
            <i class="ph-fill ph-medal text-amber-500 text-sm"></i>
            <span>Бесплатный пожизненный доступ <strong class="text-slate-700 dark:text-slate-200">Founding Member</strong> для авторов валидных идей</span>
        </div>
    </footer>

</div>

<script>
        // Функция переключения светлой и темной темы
        function toggleTheme() {
            const html = document.documentElement;
            const icon = document.getElementById('theme-icon');
            
            if (html.classList.contains('dark')) {
                html.classList.remove('dark');
                html.classList.add('light');
                icon.className = 'ph-bold ph-sun text-lg';
                localStorage.setItem('yasno_theme', 'light');
            } else {
                html.classList.remove('light');
                html.classList.add('dark');
                icon.className = 'ph-bold ph-moon text-lg';
                localStorage.setItem('yasno_theme', 'dark');
            }
        }

        // Логика чата ИИ
        const chatMessages = document.getElementById('chat-messages');
        const chatInput = document.getElementById('chat-input');

        const knowledgeBase = {
            "что с золотом?": "По золоту (XAU/USD) зафиксирован режим <b>«Бычий шторм»</b>. Наблюдается сильный импульс с пробоем максимумов сессии. Трендовые алгоритмы ищут сетапы на покупку (Pullback) при откатном движении.",
            "почему сработал бот 1?": "<b>Бот #1 (Impulse Pullback)</b> активировался, так как рыночные условия Золота полностью соответствуют его профилю — «Бычий шторм». Он успешно вошел на откате после слома структуры на M15 со сбалансированным Risk/Reward.",
            "объясни последний сбой": "Сбой (-1 R) произошел во время выхода блока новостей США. Резкий спайк волатильности задел стоп-лосс до возобновления основного движения. Это штатная погрешность при работе алгоритмов в момент турбулентности.",
            "default": "Я отслеживаю показатели платформы Yasno.trade. Вы можете спросить меня о состоянии Золота/Серебра, эффективности ботов или причинах активации конкретной модели."
        };

        function addMessage(text, isUser = false) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `flex gap-3 max-w-[85%] message-anim ${isUser ? 'ml-auto flex-row-reverse' : ''}`;
            
            const avatarHtml = isUser 
                ? `<div class="w-8 h-8 rounded-lg bg-slate-800 text-white dark:bg-slate-200 dark:text-slate-900 flex-shrink-0 flex items-center justify-center font-bold text-xs mt-0.5 shadow-sm"><i class="ph-bold ph-user"></i></div>`
                : `<div class="w-8 h-8 rounded-lg bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 flex-shrink-0 flex items-center justify-center font-bold text-xs mt-0.5 shadow-sm"><i class="ph-bold ph-sparkle"></i></div>`;
            
            const bubbleHtml = `
                <div class="${isUser 
                    ? 'bg-cyan-600 text-white rounded-tr-sm' 
                    : 'bg-white dark:bg-slate-800 border border-slate-200/80 dark:border-white/10 rounded-tl-sm text-slate-800 dark:text-slate-100'} border rounded-2xl px-4 py-3 text-xs sm:text-sm leading-relaxed shadow-sm">
                    ${text}
                </div>
            `;

            msgDiv.innerHTML = avatarHtml + bubbleHtml;
            chatMessages.appendChild(msgDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function simulateAIResponse(query) {
            // Индикатор набора ответа
            const typingDiv = document.createElement('div');
            typingDiv.id = 'typing-indicator';
            typingDiv.className = 'flex gap-3 max-w-[85%] message-anim';
            typingDiv.innerHTML = `
                <div class="w-8 h-8 rounded-lg bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 flex-shrink-0 flex items-center justify-center font-bold text-xs mt-0.5"><i class="ph-bold ph-sparkle"></i></div>
                <div class="bg-white dark:bg-slate-800 border border-slate-200/80 dark:border-white/10 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1.5 shadow-sm">
                    <div class="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                </div>
            `;
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            setTimeout(() => {
                const indicator = document.getElementById('typing-indicator');
                if (indicator) indicator.remove();
                
                const lowerQuery = query.toLowerCase().trim();
                let response = knowledgeBase["default"];
                
                for (const key in knowledgeBase) {
                    if (lowerQuery.includes(key.toLowerCase())) {
                        response = knowledgeBase[key];
                        break;
                    }
                }
                
                addMessage(response, false);
            }, 700 + Math.random() * 400);
        }

        function handleSend() {
            const text = chatInput.value.trim();
            if (text) {
                addMessage(text, true);
                chatInput.value = '';
                simulateAIResponse(text);
            }
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') {
                handleSend();
            }
        }

        function sendPrompt(text) {
        addMessage(text, true);
        simulateAIResponse(text);
    }

    // --- НОВЫЙ ИНТЕРАКТИВНЫЙ ФУНКЦИОНАЛ ---

    // 1. Переключение периодов профита
    function setPeriod(btn, period, value) {
        // Убираем активный класс у всех кнопок
        document.querySelectorAll('.period-btn').forEach(b => {
            b.classList.remove('bg-white', 'dark:bg-slate-700', 'text-slate-800', 'dark:text-white', 'shadow-sm', 'active-period');
            b.classList.add('text-slate-500', 'dark:text-slate-400');
        });
        // Добавляем нажатой кнопке
        btn.classList.add('bg-white', 'dark:bg-slate-700', 'text-slate-800', 'dark:text-white', 'shadow-sm', 'active-period');
        btn.classList.remove('text-slate-500', 'dark:text-slate-400');
        
        // Анимация смены числа
        const valEl = document.getElementById('total-profit-val');
        valEl.style.opacity = '0';
        setTimeout(() => {
            valEl.innerText = `+${value} R`;
            valEl.style.opacity = '1';
        }, 200);
    }

    // 2. Drill-down для ботов (Раскрывающийся аккордеон)
    function toggleBotDetails(botId) {
        const details = document.getElementById(`${botId}-details`);
        const icon = document.getElementById(`${botId}-icon`);
        if (!details) return;
        
        if (details.classList.contains('open')) {
            details.classList.remove('open');
            if(icon) icon.style.transform = 'rotate(0deg)';
        } else {
            details.classList.add('open');
            if(icon) icon.style.transform = 'rotate(180deg)';
        }
    }

    // 3. Проактивный ИИ (Push-инсайт)
    window.addEventListener('DOMContentLoaded', () => {
        // Имитация события, когда ИИ сам решает дать инсайт через 3 секунды после загрузки
        setTimeout(() => {
            const toast = document.getElementById('proactive-toast');
            if (toast) {
                toast.style.display = 'flex';
            }
        }, 3000); 
    });

</script>
</body>
</html>