"""Погода рынка по закрытым часовикам H1: структура + ширина коридора."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from public_market import fetch_h1

OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "lab_weather.json"
BARS = 200
TAPE = 36
SWING_L = 2
ATR_N = 14
RANGE_N = 24
NARROW_ATR = 2.8
WIDE_ATR = 5.5
ADX_N = 14
ADX_WEAK = 20.0
ADX_MEDIUM = 35.0
ADX_STORM = 50.0

ASSETS = (
    {"key": "xau", "symbol": "XAUUSD", "name": "Золото", "digits": 2},
    {"key": "xag", "symbol": "XAGUSD", "name": "Серебро", "digits": 3},
)

MONTHS_RU = (
    "янв", "фев", "мар", "апр", "май", "июн",
    "июл", "авг", "сен", "окт", "ноя", "дек",
)


def _fmt_price(value: float, digits: int) -> str:
    return f"{value:.{digits}f}"


def _fmt_when(ts: datetime) -> str:
    return f"{ts.day} {MONTHS_RU[ts.month - 1]}, {ts.strftime('%H:%M')}"


def _fetch_h1(asset_key: str) -> list[dict]:
    bars = fetch_h1(asset_key)
    if len(bars) > BARS:
        return bars[-BARS:]
    return bars


def _swings(bars: list[dict], kind: str) -> list[dict]:
    found = []
    last = len(bars) - 1 - SWING_L
    for i in range(SWING_L, last + 1):
        window = bars[i - SWING_L : i + SWING_L + 1]
        if kind == "high":
            peak = bars[i]["high"]
            if all(peak >= bar["high"] for bar in window) and peak > bars[i - 1]["high"] and peak > bars[i + 1]["high"]:
                found.append({"index": i, "price": peak, "time": bars[i]["time"]})
        else:
            trough = bars[i]["low"]
            if all(trough <= bar["low"] for bar in window) and trough < bars[i - 1]["low"] and trough < bars[i + 1]["low"]:
                found.append({"index": i, "price": trough, "time": bars[i]["time"]})
    return found


def _atr(bars: list[dict]) -> float:
    trs = []
    start = max(1, len(bars) - ATR_N)
    for i in range(start, len(bars)):
        prev_close = bars[i - 1]["close"]
        high, low = bars[i]["high"], bars[i]["low"]
        trs.append(max(high - low, abs(high - prev_close), abs(low - prev_close)))
    return sum(trs) / len(trs) if trs else 0.0


def _adx(bars: list[dict], period: int = ADX_N) -> dict:
    empty = {"adx": 0.0, "plus_di": 0.0, "minus_di": 0.0}
    if len(bars) < period + 2:
        return empty
    plus_dm, minus_dm, tr = [], [], []
    for i in range(1, len(bars)):
        up = bars[i]["high"] - bars[i - 1]["high"]
        down = bars[i - 1]["low"] - bars[i]["low"]
        plus_dm.append(up if up > down and up > 0 else 0.0)
        minus_dm.append(down if down > up and down > 0 else 0.0)
        prev_c = bars[i - 1]["close"]
        high, low = bars[i]["high"], bars[i]["low"]
        tr.append(max(high - low, abs(high - prev_c), abs(low - prev_c)))
    dx_vals = []
    plus_last = minus_last = 0.0
    for i in range(period - 1, len(tr)):
        window = slice(i + 1 - period, i + 1)
        atr = sum(tr[window]) / period
        pdi = (100 * sum(plus_dm[window]) / period / atr) if atr else 0.0
        mdi = (100 * sum(minus_dm[window]) / period / atr) if atr else 0.0
        plus_last, minus_last = pdi, mdi
        denom = pdi + mdi
        dx_vals.append((100 * abs(pdi - mdi) / denom) if denom else 0.0)
    if len(dx_vals) < period:
        return empty
    return {
        "adx": round(sum(dx_vals[-period:]) / period, 1),
        "plus_di": round(plus_last, 1),
        "minus_di": round(minus_last, 1),
    }


def _extreme_since(bars: list[dict], start: int, kind: str) -> dict:
    best_i = start
    if kind == "high":
        best = bars[start]["high"]
        for i in range(start, len(bars)):
            if bars[i]["high"] >= best:
                best = bars[i]["high"]
                best_i = i
        return {"index": best_i, "price": best, "time": bars[best_i]["time"]}
    best = bars[start]["low"]
    for i in range(start, len(bars)):
        if bars[i]["low"] <= best:
            best = bars[i]["low"]
            best_i = i
    return {"index": best_i, "price": best, "time": bars[best_i]["time"]}


def _classify(bars: list[dict], digits: int) -> dict:
    highs = _swings(bars, "high")
    lows = _swings(bars, "low")
    close = bars[-1]["close"]
    last_high = highs[-1] if highs else None
    prev_high = highs[-2] if len(highs) >= 2 else None
    last_low = lows[-1] if lows else None
    prev_low = lows[-2] if len(lows) >= 2 else None

    hh = last_high and prev_high and last_high["price"] > prev_high["price"]
    hl = last_low and prev_low and last_low["price"] > prev_low["price"]
    lh = last_high and prev_high and last_high["price"] < prev_high["price"]
    ll = last_low and prev_low and last_low["price"] < prev_low["price"]
    holds_up = last_low and close > last_low["price"]
    holds_down = last_high and close < last_high["price"]

    if hh and hl and holds_up:
        direction, direction_label = "up", "Восход"
        regime = "Тренд вверх"
    elif lh and ll and holds_down:
        direction, direction_label = "down", "Спуск"
        regime = "Тренд вниз"
    else:
        direction, direction_label = "side", "Боковик"
        regime = "Боковик"

    if direction == "up" and last_low:
        last_high = _extreme_since(bars, last_low["index"], "high")
    elif direction == "down" and last_high:
        last_low = _extreme_since(bars, last_high["index"], "low")

    window = bars[-RANGE_N:]
    range_n = max(bar["high"] for bar in window) - min(bar["low"] for bar in window)
    atr = _atr(bars)
    ratio = range_n / atr if atr else 0.0
    dmi = _adx(bars)
    adx = dmi["adx"]
    if adx < ADX_WEAK:
        band, adx_label = "weak", "слабый"
    elif adx < ADX_MEDIUM:
        band, adx_label = "medium", "средний"
    elif adx < ADX_STORM:
        band, adx_label = "strong", "сильный"
    else:
        band, adx_label = "extreme", "шторм"

    if band == "weak":
        weather, weather_label = "calm", "штиль"
        energy = "narrow"
    elif direction == "side":
        weather, weather_label = ("front", "фронт") if band in {"strong", "extreme"} else ("calm", "штиль")
        energy = "wide" if band in {"strong", "extreme"} else "narrow"
    elif band == "extreme":
        weather, weather_label = "storm", "шторм"
        energy = "wide"
    elif band == "strong":
        weather, weather_label = "strong", "сильный"
        energy = "wide"
    else:
        weather, weather_label = "wind", "ветер"
        energy = "normal"

    if direction == "side":
        move_label = {
            "weak": "коридор узкий",
            "medium": "коридор обычный",
            "strong": "коридор широкий",
            "extreme": "коридор широкий",
        }[band]
    else:
        move_label = {
            "weak": "ход слабый",
            "medium": "ход средний",
            "strong": "ход сильный",
            "extreme": "ход очень сильный",
        }[band]
    energy_label = adx_label

    wx_note = {
        "storm": " — шторм",
        "calm": " — штиль",
        "front": " — фронт",
        "wind": "",
        "strong": "",
    }[weather]
    summary = f"{regime}. {move_label[0].upper() + move_label[1:]}{wx_note}."

    position, position_label = "unknown", "нет пары якорей"
    if last_high and close >= last_high["price"]:
        position, position_label = "above_high", "выше последнего max"
    elif last_low and close <= last_low["price"]:
        position, position_label = "below_low", "ниже последнего min"
    elif last_high and last_low and last_high["price"] > last_low["price"]:
        pos = (close - last_low["price"]) / (last_high["price"] - last_low["price"])
        if pos >= 0.66:
            position, position_label = "near_high", "у последнего max"
        elif pos <= 0.34:
            position, position_label = "near_low", "у последнего min"
        else:
            position, position_label = "middle", "между max и min"

    tape_start = max(0, len(bars) - TAPE)
    if last_high:
        tape_start = min(tape_start, last_high["index"])
    if last_low:
        tape_start = min(tape_start, last_low["index"])
    tape_start = max(0, min(tape_start, len(bars) - 24))
    tape = bars[tape_start:]
    closes = [bar["close"] for bar in tape]
    extra = []
    high_i = last_high["index"] - tape_start if last_high else None
    low_i = last_low["index"] - tape_start if last_low else None
    if last_high:
        extra.append(last_high["price"])
    if last_low:
        extra.append(last_low["price"])
    lo_p = min(closes + extra)
    hi_p = max(closes + extra)
    span = hi_p - lo_p or 1.0

    def xy(i: int, price: float) -> tuple[float, float]:
        x = 5 + (90 * i / max(len(tape) - 1, 1))
        y = 26 - ((price - lo_p) / span) * 22
        return x, y

    coords = [xy(i, price) for i, price in enumerate(closes)]
    line = "M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    spark = {"line": line, "area": f"{line} L{coords[-1][0]:.1f},30 L5,30 Z"}
    if last_high and high_i is not None and 0 <= high_i < len(tape):
        x, y = xy(high_i, last_high["price"])
        spark["high"] = {"x": round(x, 1), "y": round(y, 1)}
    if last_low and low_i is not None and 0 <= low_i < len(tape):
        x, y = xy(low_i, last_low["price"])
        spark["low"] = {"x": round(x, 1), "y": round(y, 1)}
    badge = f"{direction_label} · {weather_label}"

    def swing_payload(swing: dict | None) -> dict | None:
        if not swing:
            return None
        return {
            "price": round(swing["price"], digits),
            "price_text": _fmt_price(swing["price"], digits),
            "time": swing["time"].strftime("%Y-%m-%dT%H:%M:%S"),
            "label": _fmt_when(swing["time"]),
        }

    return {
        "close": round(close, digits),
        "close_text": _fmt_price(close, digits),
        "direction": direction,
        "direction_label": direction_label,
        "regime": regime,
        "energy": energy,
        "energy_label": energy_label,
        "move_label": move_label,
        "weather": weather,
        "weather_label": weather_label,
        "badge": badge,
        "summary": summary,
        "last_high": swing_payload(last_high),
        "last_low": swing_payload(last_low),
        "position": position,
        "position_label": position_label,
        "range_atr": round(ratio, 2),
        "adx": adx,
        "adx_band": band,
        "adx_label": adx_label,
        "plus_di": dmi["plus_di"],
        "minus_di": dmi["minus_di"],
        "adx_bar_pct": round(min(adx / ADX_STORM, 1.0) * 100, 1),
        "sparkline": spark,
        "last_bar": bars[-1]["time"].strftime("%Y-%m-%dT%H:%M:%S"),
    }


def collect() -> dict:
    now = datetime.now()
    assets = {}
    for spec in ASSETS:
        bars = _fetch_h1(spec["key"])
        payload = _classify(bars, spec["digits"])
        payload.update({"symbol": spec["symbol"], "name": spec["name"]})
        payload["tick"] = {
            "price": payload["close"],
            "price_text": payload["close_text"],
            "time": payload["last_bar"],
        }
        assets[spec["key"]] = payload

    xau, xag = assets["xau"], assets["xag"]
    focus = (
        f"Золото: {xau['regime'].lower()}, {xau['move_label']}. "
        f"Серебро: {xag['regime'].lower()}, {xag['move_label']}."
    )
    return {
        "updated_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "updated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "public:H1:yahoo",
        "focus": focus,
        "xau": xau,
        "xag": xag,
    }


def main():
    snapshot = collect()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    print(f"XAU {snapshot['xau']['badge']} | {snapshot['xau']['summary']}")
    print(f"XAG {snapshot['xag']['badge']} | {snapshot['xag']['summary']}")
    print(snapshot["focus"])


if __name__ == "__main__":
    main()
