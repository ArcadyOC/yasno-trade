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
                    <h1 class="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white flex items-center gap-1.5">
                        Yasno<span class="text-cyan-600 dark:text-cyan-400 font-semibold">.trade</span>
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

                <!-- Переключатель режима Просто / Quant -->
                <div class="flex items-center bg-slate-200/60 dark:bg-slate-800/80 rounded-full p-1 border border-slate-300/40 dark:border-white/5">
                    <button class="px-3.5 py-1 rounded-full text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white transition-all">Просто</button>
                    <button class="px-3.5 py-1 rounded-full bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm font-bold border border-slate-200/80 dark:border-white/10">Quant</button>
                </div>

                <!-- Кнопка переключения темы Light / Dark -->
                <button onclick="toggleTheme()" id="theme-toggle" title="Сменить тему оформления" 
                        class="p-2 rounded-xl bg-slate-200/60 dark:bg-slate-800/80 hover:bg-slate-300/60 dark:hover:bg-slate-700 text-slate-700 dark:text-amber-400 transition-colors border border-slate-300/40 dark:border-white/10 flex items-center justify-center">
                    <i id="theme-icon" class="ph-bold ph-sun text-lg"></i>
                </button>
            </div>
        </header>

        <!-- TOP METRICS (Hero Bar) -->
        <section class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <!-- Совокупный R-профит -->
            <div class="glass-panel p-5 flex flex-col items-center text-center relative overflow-hidden group">
                <div class="absolute -right-6 -top-6 w-24 h-24 bg-emerald-400/10 rounded-full blur-xl group-hover:scale-150 transition-transform"></div>
                <span class="text-xs font-bold text-slate-400 dark:text-slate-400 uppercase tracking-wider mb-1">Суммарный профит</span>
                <span class="text-3xl sm:text-4xl font-extrabold text-emerald-600 dark:text-emerald-400 tracking-tight">+148.5 R</span>
                <span class="text-[11px] font-medium text-emerald-700/70 dark:text-emerald-400/70 mt-1 flex items-center gap-1">
                    <i class="ph-bold ph-trend-up"></i> Высокий темп прироста
                </span>
            </div>

            <!-- Индекс реализации -->
            <div class="glass-panel p-5 flex flex-col items-center text-center relative overflow-hidden group">
                <div class="absolute -right-6 -top-6 w-24 h-24 bg-cyan-400/10 rounded-full blur-xl group-hover:scale-150 transition-transform"></div>
                <span class="text-xs font-bold text-slate-400 dark:text-slate-400 uppercase tracking-wider mb-1">Индекс реализации</span>
                <span class="text-3xl sm:text-4xl font-extrabold text-slate-800 dark:text-white tracking-tight">69.4%</span>
                <span class="text-[11px] font-medium text-slate-500 dark:text-slate-400 mt-1">Точность сигналов системы</span>
            </div>

            <!-- Активные агенты -->
            <div class="glass-panel p-5 flex flex-col items-center text-center relative overflow-hidden group">
                <div class="absolute -right-6 -top-6 w-24 h-24 bg-indigo-400/10 rounded-full blur-xl group-hover:scale-150 transition-transform"></div>
                <span class="text-xs font-bold text-slate-400 dark:text-slate-400 uppercase tracking-wider mb-1">Активные агенты</span>
                <span class="text-3xl sm:text-4xl font-extrabold text-cyan-600 dark:text-cyan-400 tracking-tight flex items-baseline gap-2">
                    5 <span class="text-base font-semibold text-slate-400 dark:text-slate-400">Онлайн</span>
                </span>
                <span class="text-[11px] font-medium text-cyan-700/70 dark:text-cyan-400/70 mt-1 flex items-center gap-1">
                    <i class="ph-bold ph-cpu"></i> Все системы синхронизированы
                </span>
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
                        <div class="flex justify-between items-start mb-2">
                            <div>
                                <span class="text-xs font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider">XAU / USD</span>
                                <h3 class="font-bold text-base text-slate-900 dark:text-white">Золото</h3>
                            </div>
                            <span class="inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-lg bg-emerald-500 text-white shadow-sm shadow-emerald-500/30">
                                <i class="ph-bold ph-lightning"></i> Бычий шторм
                            </span>
                        </div>
                        <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 font-medium leading-relaxed">
                            Мощный восходящий импульс. В приоритете трендовые модели на покупку на локальных откатах.
                        </p>
                    </div>

                    <!-- Карточка Серебра (XAG/USD) -->
                    <div class="glass-panel p-4 border border-cyan-200/80 dark:border-cyan-500/30 bg-cyan-50/40 dark:bg-cyan-900/10 rounded-2xl relative overflow-hidden group transition-all">
                        <div class="flex justify-between items-start mb-2">
                            <div>
                                <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">XAG / USD</span>
                                <h3 class="font-bold text-base text-slate-900 dark:text-white">Серебро</h3>
                            </div>
                            <span class="inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-lg bg-cyan-500 text-white shadow-sm shadow-cyan-500/30">
                                <i class="ph-bold ph-waves"></i> Штиль
                            </span>
                        </div>
                        <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 font-medium leading-relaxed">
                            Узкий боковой диапазон. Активированы алгоритмы работы от границ коридора (Mean Reversion).
                        </p>
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
                    <div class="glass-panel p-4 text-slate-800 dark:text-white glow-active relative flex flex-col gap-3 glass-panel-hover bg-white/90 dark:bg-slate-800/90">
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
                        <div class="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 tracking-tight">+42.0 R</div>
                        <div class="text-xs font-medium text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5 pt-2 border-t border-slate-100 dark:border-white/5">
                            <i class="ph-bold ph-check-circle text-base"></i> Идеально совпадает с «Бычьим штормом»
                        </div>
                    </div>

                    <!-- Бот 2 (Ожидание) -->
                    <div class="glass-panel p-4 text-slate-800 dark:text-white flex flex-col gap-3 glass-panel-hover">
                        <div class="flex justify-between items-start">
                            <div>
                                <h3 class="font-bold text-base text-slate-900 dark:text-white">Бот #2</h3>
                                <span class="text-xs font-medium text-slate-500 dark:text-slate-400">RSI Divergence</span>
                            </div>
                            <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400 border border-amber-300/60 dark:border-amber-500/30">
                                Ожидание
                            </span>
                        </div>
                        <div class="text-3xl font-extrabold text-slate-800 dark:text-white tracking-tight">+18.5 R</div>
                        <div class="text-xs font-medium text-amber-700 dark:text-amber-400 flex items-center gap-1.5 pt-2 border-t border-slate-100 dark:border-white/5">
                            <i class="ph-bold ph-hourglass-high text-base"></i> Ждет смены фазы волатильности
                        </div>
                    </div>

                    <!-- Бот 3 (Активен) -->
                    <div class="glass-panel p-4 text-slate-800 dark:text-white flex flex-col gap-3 glass-panel-hover">
                        <div class="flex justify-between items-start">
                            <div>
                                <h3 class="font-bold text-base text-slate-900 dark:text-white">Бот #3</h3>
                                <span class="text-xs font-medium text-slate-500 dark:text-slate-400">Structure Break</span>
                            </div>
                            <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-cyan-100 dark:bg-cyan-900/40 text-cyan-700 dark:text-cyan-300 border border-cyan-300/60 dark:border-cyan-500/30">
                                Активен
                            </span>
                        </div>
                        <div class="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 tracking-tight">+31.2 R</div>
                        <div class="text-xs font-medium text-slate-500 dark:text-slate-400 flex items-center gap-1.5 pt-2 border-t border-slate-100 dark:border-white/5">
                            <i class="ph-bold ph-activity text-base text-cyan-500"></i> Сканирует пробой на M15
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
            <div id="chat-messages" class="p-6 flex flex-col gap-4 h-72 overflow-y-auto custom-scrollbar bg-slate-50/50 dark:bg-slate-950/20">
                <!-- Сообщение от ИИ -->
                <div class="flex gap-3 max-w-[85%]">
                    <div class="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 flex-shrink-0 flex items-center justify-center mt-0.5">
                        <i class="ph-bold ph-sparkle text-base"></i>
                    </div>
                    <div class="bg-white dark:bg-slate-800 border border-slate-200/80 dark:border-white/10 rounded-2xl rounded-tl-sm px-4 py-3 text-xs sm:text-sm text-slate-700 dark:text-slate-200 leading-relaxed shadow-sm">
                        Здравствуйте! Я ваш аналитический ассистент. Могу объяснить текущую «погоду рынка» по золоту/серебру, или почему Бот #1 активировался в режиме «Бычьего шторма».
                    </div>
                </div>
            </div>

            <!-- Чипы быстрых запросов (Quick Prompts) -->
            <div class="px-6 py-2.5 bg-white/40 dark:bg-slate-900/40 border-t border-slate-200/60 dark:border-white/5 flex flex-wrap gap-2" id="quick-prompts">
                <button onclick="sendPrompt(this.innerText)" class="px-3 py-1.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-white/10 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:border-cyan-500 hover:text-cyan-600 dark:hover:text-cyan-400 shadow-sm transition-all flex items-center gap-1.5">
                    <i class="ph-bold ph-lightning text-amber-500"></i> Что с золотом?
                </button>
                <button onclick="sendPrompt(this.innerText)" class="px-3 py-1.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-white/10 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:border-cyan-500 hover:text-cyan-600 dark:hover:text-cyan-400 shadow-sm transition-all flex items-center gap-1.5">
                    <i class="ph-bold ph-robot text-emerald-500"></i> Почему сработал Бот 1?
                </button>
                <button onclick="sendPrompt(this.innerText)" class="px-3 py-1.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-white/10 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:border-cyan-500 hover:text-cyan-600 dark:hover:text-cyan-400 shadow-sm transition-all flex items-center gap-1.5">
                    <i class="ph-bold ph-warning-circle text-rose-500"></i> Объясни последний сбой
                </button>
            </div>

            <!-- Поле ввода вопроса -->
            <div class="p-4 bg-white/80 dark:bg-slate-900/80 border-t border-slate-200/80 dark:border-white/10">
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
        <footer class="mt-2 mb-8 flex flex-col items-center gap-3.5 text-center">
            <button class="group relative px-6 py-3.5 bg-white dark:bg-slate-800 border border-slate-200/90 dark:border-white/10 rounded-2xl flex items-center gap-2.5 hover:border-emerald-500 shadow-lg shadow-slate-200/50 dark:shadow-none transition-all overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/0 via-emerald-500/10 to-emerald-500/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
                <div class="w-7 h-7 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">
                    <i class="ph-bold ph-lightbulb text-lg"></i>
                </div>
                <span class="font-bold text-sm text-slate-800 dark:text-white">+ Предложить свою гипотезу</span>
            </button>
            
            <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center justify-center gap-1.5">
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
    </script>
</body>
</html>