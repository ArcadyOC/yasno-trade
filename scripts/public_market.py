"""Котировки золота и серебра из открытых источников — без терминала."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = {"User-Agent": "YasnoLab/1.0", "Accept": "application/json"}
WEATHER_PATH = Path(__file__).resolve().parents[1] / "data" / "lab_weather.json"
SPOT = {
    "xau": ("https://api.gold-api.com/price/XAU", 2, "XAUUSD"),
    "xag": ("https://api.gold-api.com/price/XAG", 3, "XAGUSD"),
}
YAHOO = {"xau": "GC=F", "xag": "SI=F"}


def _http_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"источник не ответил ({err.code})") from err
    except urllib.error.URLError as err:
        raise RuntimeError("источник недоступен") from err


def _fmt(price: float, digits: int) -> str:
    return f"{price:.{digits}f}"


def _from_gold_api(asset_key: str) -> dict:
    url, digits, symbol = SPOT[asset_key]
    data = _http_json(url)
    price = float(data.get("price") or 0)
    if price <= 0:
        raise RuntimeError("пустая цена")
    stamp = str(data.get("updatedAt") or "")
    when = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if stamp:
        try:
            when = (
                datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                .astimezone(timezone.utc)
                .replace(tzinfo=None)
                .strftime("%Y-%m-%dT%H:%M:%S")
            )
        except ValueError:
            pass
    return {
        "symbol": symbol,
        "price": round(price, digits),
        "price_text": _fmt(price, digits),
        "time": when,
    }


def _from_yahoo_spot(asset_key: str) -> dict:
    ticker = YAHOO[asset_key]
    _, digits, symbol = SPOT[asset_key]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
    data = _http_json(url)
    result = ((data.get("chart") or {}).get("result") or [None])[0]
    if not result:
        raise RuntimeError("yahoo пустой")
    meta = result.get("meta") or {}
    price = float(meta.get("regularMarketPrice") or 0)
    if price <= 0:
        raise RuntimeError("yahoo без цены")
    raw_ts = meta.get("regularMarketTime")
    when = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if raw_ts:
        when = datetime.fromtimestamp(int(raw_ts), timezone.utc).replace(tzinfo=None).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
    return {
        "symbol": symbol,
        "price": round(price, digits),
        "price_text": _fmt(price, digits),
        "time": when,
    }


def _from_weather(asset_key: str) -> dict | None:
    try:
        data = json.loads(WEATHER_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    asset = data.get(asset_key) if isinstance(data, dict) else None
    if not isinstance(asset, dict):
        return None
    tick = asset.get("tick") if isinstance(asset.get("tick"), dict) else {}
    price = tick.get("price_text") or asset.get("close_text")
    if not price:
        return None
    _, _, symbol = SPOT[asset_key]
    try:
        numeric = float(str(price).replace(" ", "").replace(",", "."))
    except ValueError:
        return None
    return {
        "symbol": symbol,
        "price": numeric,
        "price_text": str(price),
        "time": str(tick.get("time") or asset.get("last_bar") or data.get("updated_at") or ""),
    }


def fetch_tick(asset_key: str) -> dict:
    try:
        return _from_yahoo_spot(asset_key)
    except RuntimeError:
        cached = _from_weather(asset_key)
        if cached:
            return cached
        return _from_gold_api(asset_key)


def fetch_ticks() -> dict:
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    out = {"updated_at": now, "source": "public:yahoo"}
    for key in SPOT:
        try:
            out[key] = fetch_tick(key)
        except RuntimeError:
            out[key] = None
    return out


def fetch_h1(asset_key: str) -> list[dict]:
    ticker = YAHOO[asset_key]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1h&range=1mo"
    data = _http_json(url)
    result = ((data.get("chart") or {}).get("result") or [None])[0]
    if not result:
        raise RuntimeError(f"{ticker}: нет часовиков")
    stamps = result.get("timestamp") or []
    quote = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    opens = quote.get("open") or []
    highs = quote.get("high") or []
    lows = quote.get("low") or []
    closes = quote.get("close") or []
    rows: list[dict] = []
    for i, stamp in enumerate(stamps):
        if i >= len(opens) or i >= len(highs) or i >= len(lows) or i >= len(closes):
            break
        o, h, l, c = opens[i], highs[i], lows[i], closes[i]
        if None in (o, h, l, c):
            continue
        rows.append(
            {
                "time": datetime.fromtimestamp(int(stamp), timezone.utc).replace(tzinfo=None),
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
            }
        )
    if len(rows) < 40:
        raise RuntimeError(f"{ticker}: мало часовиков ({len(rows)})")
    return rows[:-1] if len(rows) > 40 else rows
