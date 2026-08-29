"""Локальный сервер дашборда: HTML + живые тики MT5 + ключ исследователя."""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import MetaTrader5 as mt5

from hypothesis_run import run_hypothesis
from lab_llm import ask_lab, api_key as llm_key
from lab_users import (
    change_energy,
    find_user,
    init_user,
    lab_pulse,
    log_hypothesis_run,
    set_nickname,
)

ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"
PORT = 8765
SYMBOLS = (("xau", "XAUUSD", 2), ("xag", "XAGUSD", 3))

# Публичный доступ: гости и так ограничены энергией (10 действий на IP без
# пополнения), но это не страхует от суммарного расхода платного ключа ИИ,
# если ссылку откроют много разных людей сразу. Дневной потолок — общий
# предохранитель поверх личных лимитов.
AI_USAGE_PATH = ROOT / "data" / "ai_usage_daily.json"
AI_DAILY_LIMIT = 60

TICKS_TTL = 2.0
_ticks_cache: dict = {"data": None, "at": 0.0}
_ticks_lock = threading.Lock()


def _ai_usage_load() -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        data = json.loads(AI_USAGE_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    if data.get("date") != today:
        data = {"date": today, "count": 0}
    return data


def _ai_usage_bump() -> None:
    data = _ai_usage_load()
    data["count"] = int(data.get("count", 0)) + 1
    AI_USAGE_PATH.write_text(json.dumps(data), encoding="utf-8")


def _json_bytes(payload: dict, status: int, handler: SimpleHTTPRequestHandler) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _bearer(handler: SimpleHTTPRequestHandler) -> str | None:
    raw = handler.headers.get("Authorization") or ""
    if raw.lower().startswith("bearer "):
        key = raw[7:].strip()
        return key or None
    return None


def _read_json(handler: SimpleHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length") or 0)
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _ticks() -> dict:
    if not mt5.initialize():
        raise RuntimeError(str(mt5.last_error()))
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    out = {"updated_at": now, "source": "mt5:tick"}
    try:
        for key, symbol, digits in SYMBOLS:
            info = mt5.symbol_info_tick(symbol)
            if info is None:
                out[key] = None
                continue
            price = float(info.bid or info.last or 0)
            out[key] = {
                "symbol": symbol,
                "price": round(price, digits),
                "price_text": f"{price:.{digits}f}",
                "time": datetime.fromtimestamp(int(info.time), timezone.utc)
                .replace(tzinfo=None)
                .strftime("%Y-%m-%dT%H:%M:%S"),
            }
    finally:
        mt5.shutdown()
    return out


def _ticks_cached() -> dict:
    now = time.monotonic()
    with _ticks_lock:
        cached = _ticks_cache["data"]
        if cached is not None and now - _ticks_cache["at"] < TICKS_TTL:
            return cached
    data = _ticks()
    with _ticks_lock:
        _ticks_cache["data"] = data
        _ticks_cache["at"] = now
    return data


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def guess_type(self, path):
        if path.replace("\\", "/").endswith("dashlitefin.html"):
            return "text/html; charset=utf-8"
        return super().guess_type(path)

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/":
            self.send_response(302)
            self.send_header("Location", "/dashlitefin.html")
            self.end_headers()
            return
        if route == "/api/ticks":
            try:
                _json_bytes(_ticks_cached(), 200, self)
            except Exception as err:
                _json_bytes({"error": str(err)}, 503, self)
            return
        if route == "/api/me":
            user = find_user(_bearer(self))
            if not user:
                _json_bytes({"error": "Нет такого пропуска. Открой страницу заново или вставь ключ."}, 401, self)
                return
            _json_bytes(user, 200, self)
            return
        if route == "/api/lab-pulse":
            _json_bytes(lab_pulse(), 200, self)
            return
        return super().do_GET()

    def do_POST(self):
        route = urlparse(self.path).path
        if route == "/api/init-user":
            status, payload = init_user(_bearer(self), self.client_address[0])
            _json_bytes(payload, status, self)
            return
        if route == "/api/test-idea":
            key = _bearer(self)
            preview = find_user(key)
            if not preview:
                _json_bytes({"error": "Нет такого пропуска. Открой страницу заново или вставь ключ."}, 401, self)
                return
            cost = int(preview.get("action_cost") or 0)
            spent, user = change_energy(key, -cost)
            if spent != 200:
                _json_bytes(user, spent, self)
                return
            body = _read_json(self)
            try:
                report = run_hypothesis(
                    str(body.get("symbol") or "xau"),
                    str(body.get("pattern") or "sweep"),
                    str(body.get("timeframe") or "m15"),
                    float(body.get("target_r") or 2.0),
                    str(body.get("session") or "all"),
                    int(body.get("days") or 90),
                )
            except Exception as err:
                if cost:
                    change_energy(key, cost)
                back = find_user(key) or {}
                _json_bytes({"error": str(err), **back}, 503, self)
                return
            log_hypothesis_run(key, user.get("nickname") or "Lab", report.get("title") or "Проверка")
            _json_bytes({"user": user, "report": report, "cost": cost, "pulse": lab_pulse()}, 200, self)
            return
        if route == "/api/ask-lab":
            key = _bearer(self)
            if not llm_key():
                _json_bytes({"error": "Модель ещё не подключена. Нужен ключ на сервере."}, 503, self)
                return
            preview = find_user(key)
            if not preview:
                _json_bytes({"error": "Нет такого пропуска. Открой страницу заново или вставь ключ."}, 401, self)
                return
            if preview.get("role") != "founder" and _ai_usage_load()["count"] >= AI_DAILY_LIMIT:
                _json_bytes(
                    {"error": "Лимит вопросов к ИИ на сегодня исчерпан всеми гостями. Загляни завтра.", **preview},
                    429,
                    self,
                )
                return
            cost = int(preview.get("action_cost") or 0)
            spent, user = change_energy(key, -cost)
            if spent != 200:
                _json_bytes(user, spent, self)
                return
            body = _read_json(self)
            try:
                reply = ask_lab(str(body.get("question") or ""), body.get("context"))
            except Exception as err:
                if cost:
                    change_energy(key, cost)
                back = find_user(key) or {}
                _json_bytes({"error": str(err), **back}, 503, self)
                return
            if preview.get("role") != "founder":
                _ai_usage_bump()
            _json_bytes({"user": user, "cost": cost, "reply": reply, "model": "deepseek-v4-flash"}, 200, self)
            return
        if route == "/api/rename":
            body = _read_json(self)
            status, payload = set_nickname(_bearer(self), str(body.get("nickname") or ""))
            _json_bytes(payload, status, self)
            return
        self.send_error(404)

    def log_message(self, fmt, *args):
        return


def main():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"http://{HOST}:{PORT}/dashlitefin.html")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
