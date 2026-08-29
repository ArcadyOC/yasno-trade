"""Прогон пользовательской гипотезы по закрытым свечам."""

from __future__ import annotations

from datetime import datetime, timedelta

import MetaTrader5 as mt5
import pandas as pd

from chain_strategy import ElasticReclaimStrategy
from impulse_strategy import VolumeImpulseStrategy
from observe_strategy import SqueezeBreakoutStrategy
from pinbar_strategy import PinbarSweepStrategy
from trend_strategy import TrendPullbackStrategy

SYMBOLS = {"xau": ("XAUUSD", "Золото"), "xag": ("XAGUSD", "Серебро")}
DAYS_RU = {
    "Monday": "понедельник",
    "Tuesday": "вторник",
    "Wednesday": "среда",
    "Thursday": "четверг",
    "Friday": "пятница",
    "Saturday": "суббота",
    "Sunday": "воскресенье",
}

# ключ паттерна -> (класс стратегии, нужен ли контекст старших часов H1, название для отчёта)
PATTERNS = {
    "sweep": (PinbarSweepStrategy, True, "ложный пробой"),
    "trend": (TrendPullbackStrategy, True, "тренд"),
    "chain": (ElasticReclaimStrategy, False, "цепочка"),
    "impulse": (VolumeImpulseStrategy, False, "импульс"),
    "observe": (SqueezeBreakoutStrategy, False, "наблюдение"),
}

TIMEFRAMES = {
    "m15": {"mt5": mt5.TIMEFRAME_M15, "label": "15 минут", "bar_minutes": 15, "per_day": 96},
    "h1": {"mt5": mt5.TIMEFRAME_H1, "label": "1 час", "bar_minutes": 60, "per_day": 24},
}


def _bars(symbol: str, timeframe, count: int) -> pd.DataFrame:
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count + 1)
    if rates is None:
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df.iloc[:-1].copy()
    cols = ["time", "open", "high", "low", "close"]
    if "tick_volume" in df.columns:
        cols.append("tick_volume")
    df = df[cols]
    df.set_index("time", inplace=True)
    return df


def _in_session(stamp, session: str) -> bool:
    if session != "day":
        return True
    return 8 <= int(stamp.hour) < 17


def _facts(trades: list[dict]) -> tuple[str, str]:
    losses = [row for row in trades if row["r"] < 0]
    wins = [row for row in trades if row["r"] > 0]
    if not trades:
        return "На этой выборке вероятностей нет.", "Плюсов нет — выборка пустая."

    def cluster(rows, key):
        bags: dict[str, int] = {}
        for row in rows:
            bags[row[key]] = bags.get(row[key], 0) + 1
        if not bags:
            return None
        return max(bags, key=bags.get)

    loss_day = cluster(losses, "day")
    win_day = cluster(wins, "day")
    night = sum(1 for row in losses if row["hour"] < 8 or row["hour"] >= 17)
    minus = "Минусов на выборке нет."
    if losses:
        share = 100 * len(losses) / len(trades)
        minus = f"Минус получили {len(losses)} из {len(trades)} закрытий ({share:.0f}%)."
        if night and night >= len(losses) / 2:
            minus += f" Больше половины минусов — вне дневного окна ({night} из {len(losses)})."
        elif loss_day:
            minus += f" Чаще всего минус в {loss_day}."
    plus = "Плюсов на выборке нет."
    if wins:
        share = 100 * len(wins) / len(trades)
        plus = f"До цели дошли {len(wins)} из {len(trades)} ({share:.0f}%)."
        if win_day:
            plus += f" Чаще плюс в {win_day}."
    return minus, plus


def run_hypothesis(
    symbol_key: str,
    pattern_key: str,
    timeframe_key: str,
    target_r: float,
    session: str,
    days: int = 90,
) -> dict:
    pair = SYMBOLS.get(symbol_key)
    if not pair:
        raise ValueError("Можно проверить только золото или серебро.")
    symbol, title = pair

    pattern = PATTERNS.get(pattern_key)
    if not pattern:
        raise ValueError("Такого паттерна нет.")
    strategy_cls, needs_context, pattern_title = pattern

    tf = TIMEFRAMES.get(timeframe_key)
    if not tf:
        raise ValueError("Таймфрейм — 15 минут или 1 час.")

    if target_r not in (1.5, 2.0, 2.5):
        raise ValueError("Цель может быть 1.5, 2 или 2.5 R.")
    if session not in ("all", "day"):
        raise ValueError("Окно времени: все часы или только день.")

    if not mt5.initialize():
        raise RuntimeError("Нет связи с терминалом. Открой MetaTrader и попробуй ещё раз.")
    try:
        main_need = max(days * tf["per_day"], 800 if timeframe_key == "m15" else 400)
        main_df = _bars(symbol, tf["mt5"], main_need)
        h1 = None
        if needs_context:
            if timeframe_key == "h1":
                h1 = main_df
            else:
                h1_need = max(days * 24, 200)
                h1 = _bars(symbol, mt5.TIMEFRAME_H1, h1_need)
    finally:
        mt5.shutdown()

    if main_df.empty:
        raise RuntimeError("Не удалось взять историю свечей.")

    cutoff = main_df.index.max() - timedelta(days=days)
    main_df = main_df[main_df.index >= cutoff]

    strategy = strategy_cls()
    if needs_context:
        if h1 is None or h1.empty:
            h1 = main_df.resample("1h").agg(
                {"open": "first", "high": "max", "low": "min", "close": "last"}
            ).dropna()
        strategy.set_hourly_context(h1)
        if hasattr(strategy, "bar_minutes"):
            strategy.bar_minutes = tf["bar_minutes"]

    trades: list[dict] = []
    in_trade = False
    sl_price = tp_price = 0.0
    pending = None

    for i in range(1, len(main_df)):
        candle = main_df.iloc[i]
        stamp = main_df.index[i]
        if in_trade:
            if candle["low"] <= sl_price:
                pending["r"] = -1.0
                trades.append(pending)
                in_trade = False
            elif candle["high"] >= tp_price:
                pending["r"] = target_r
                trades.append(pending)
                in_trade = False
            continue
        if not _in_session(stamp, session):
            continue
        setup = strategy.check_setup(main_df, i)
        if not setup or setup["direction"] != "long":
            continue
        risk = setup["entry_price"] - setup["sl_price"]
        if risk <= 0:
            continue
        sl_price = setup["sl_price"]
        tp_price = setup["entry_price"] + risk * target_r
        in_trade = True
        pending = {
            "day": DAYS_RU.get(stamp.strftime("%A"), stamp.strftime("%A")),
            "hour": int(stamp.hour),
        }

    n = len(trades)
    wins = sum(1 for row in trades if row["r"] > 0)
    total_r = sum(row["r"] for row in trades)
    span_days = max((main_df.index.max() - main_df.index.min()).days, 1)
    per_week = n / (span_days / 7) if n else 0.0
    minus, plus = _facts(trades)
    session_label = "только день (08–17 UTC)" if session == "day" else "все часы"
    return {
        "title": f"{title} · {tf['label']} · {pattern_title} · цель {target_r:g} R",
        "symbol": title,
        "pattern": pattern_title,
        "timeframe": tf["label"],
        "days": days,
        "session": session_label,
        "from": main_df.index.min().strftime("%d.%m.%Y"),
        "to": main_df.index.max().strftime("%d.%m.%Y"),
        "closed": n,
        "wins": wins,
        "win_rate_pct": round(100 * wins / n, 1) if n else 0.0,
        "sum_r": round(total_r, 1),
        "ev": round(total_r / n, 2) if n else 0.0,
        "trades_per_week": round(per_week, 1),
        "minus": minus,
        "plus": plus,
        "note": "История закрытых свечей. Это не совет.",
        "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
