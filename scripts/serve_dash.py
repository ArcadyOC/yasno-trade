"""Локальный сервер дашборда: HTML + живые тики MT5 + ключ исследователя."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import MetaTrader5 as mt5

from hypothesis_run import run_hypothesis
from lab_users import (
    TEST_COST,
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


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def guess_type(self, path):
        if path.replace("\\", "/").endswith("dashlitefin.py"):
            return "text/html; charset=utf-8"
        return super().guess_type(path)

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/api/ticks":
            try:
                _json_bytes(_ticks(), 200, self)
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
            spent, user = change_energy(key, -TEST_COST)
            if spent != 200:
                _json_bytes(user, spent, self)
                return
            body = _read_json(self)
            try:
                report = run_hypothesis(
                    str(body.get("symbol") or "xau"),
                    float(body.get("target_r") or 2.0),
                    str(body.get("session") or "all"),
                    int(body.get("days") or 90),
                )
            except Exception as err:
                change_energy(key, TEST_COST)
                back = find_user(key) or {}
                _json_bytes({"error": str(err), **back}, 503, self)
                return
            log_hypothesis_run(key, user.get("nickname") or "Lab", report.get("title") or "Проверка")
            _json_bytes({"user": user, "report": report, "cost": TEST_COST, "pulse": lab_pulse()}, 200, self)
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
    print(f"http://{HOST}:{PORT}/dashlitefin.py")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
