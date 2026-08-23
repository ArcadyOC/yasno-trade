"""Прогон пользовательской гипотезы по закрытым свечам."""

from __future__ import annotations

from datetime import datetime, timedelta

import MetaTrader5 as mt5
import pandas as pd

from pinbar_strategy import PinbarSweepStrategy

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


def _bars(symbol: str, timeframe, count: int) -> pd.DataFrame:
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count + 1)
    if rates is None:
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df.iloc[:-1].copy()
    df = df[["time", "open", "high", "low", "close"]]
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


def run_hypothesis(symbol_key: str, target_r: float, session: str, days: int = 90) -> dict:
    pair = SYMBOLS.get(symbol_key)
    if not pair:
        raise ValueError("Можно проверить только золото или серебро.")
    symbol, title = pair
    if target_r not in (1.5, 2.0, 2.5):
        raise ValueError("Цель может быть 1.5, 2 или 2.5 R.")
    if session not in ("all", "day"):
        raise ValueError("Окно времени: все часы или только день.")

    if not mt5.initialize():
        raise RuntimeError("Нет связи с терминалом. Открой MetaTrader и попробуй ещё раз.")
    try:
        m15_need = max(days * 96, 800)
        h1_need = max(days * 24, 200)
        m15 = _bars(symbol, mt5.TIMEFRAME_M15, m15_need)
        h1 = _bars(symbol, mt5.TIMEFRAME_H1, h1_need)
    finally:
        mt5.shutdown()

    if m15.empty:
        raise RuntimeError("Не удалось взять историю свечей.")

    cutoff = m15.index.max() - timedelta(days=days)
    m15 = m15[m15.index >= cutoff]
    if h1.empty:
        h1 = m15.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()

    strategy = PinbarSweepStrategy()
    strategy.set_hourly_context(h1)

    trades: list[dict] = []
    in_trade = False
    sl_price = tp_price = 0.0
    pending = None

    for i in range(1, len(m15)):
        candle = m15.iloc[i]
        stamp = m15.index[i]
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
        setup = strategy.check_setup(m15, i)
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
    span_days = max((m15.index.max() - m15.index.min()).days, 1)
    per_week = n / (span_days / 7) if n else 0.0
    minus, plus = _facts(trades)
    session_label = "только день (08–17 UTC)" if session == "day" else "все часы"
    return {
        "title": f"{title} · 15 минут · пинбар · цель {target_r:g} R",
        "symbol": title,
        "days": days,
        "session": session_label,
        "from": m15.index.min().strftime("%d.%m.%Y"),
        "to": m15.index.max().strftime("%d.%m.%Y"),
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
