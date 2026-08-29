"""Сервер лаборатории: страница, котировки из открытых источников, ИИ-чат."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from collect_lab_weather import OUT_PATH as WEATHER_PATH
from collect_lab_weather import collect as collect_weather
from lab_llm import ask_lab, llm_ready, load_env
from lab_users import change_energy, find_user, init_user, lab_pulse, set_nickname
from public_market import fetch_ticks

ROOT = Path(__file__).resolve().parents[1]
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8765"))
WEATHER_EVERY_SEC = 30 * 60
TICKS_TTL = 20.0

AI_USAGE_PATH = ROOT / "data" / "ai_usage_daily.json"
AI_DAILY_LIMIT = 60

_ticks_cache: dict = {"data": None, "at": 0.0}
_ticks_lock = threading.Lock()

SECRET_NAMES = {".env", "lab_users.db"}
SECRET_DIRS = {".git", ".claude", "tmp"}


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


def _client_ip(handler: SimpleHTTPRequestHandler) -> str:
    forwarded = handler.headers.get("X-Forwarded-For") or ""
    if forwarded:
        return forwarded.split(",")[0].strip()
    return handler.client_address[0]


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


def _ticks_cached() -> dict:
    now = time.monotonic()
    with _ticks_lock:
        cached = _ticks_cache["data"]
        if cached is not None and now - _ticks_cache["at"] < TICKS_TTL:
            return cached
    data = fetch_ticks()
    with _ticks_lock:
        _ticks_cache["data"] = data
        _ticks_cache["at"] = now
    return data


def _refresh_weather() -> None:
    try:
        snapshot = collect_weather()
        WEATHER_PATH.parent.mkdir(parents=True, exist_ok=True)
        WEATHER_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        return


def _weather_loop() -> None:
    while True:
        time.sleep(WEATHER_EVERY_SEC)
        _refresh_weather()


def _is_secret(route: str) -> bool:
    parts = [p for p in route.lower().replace("\\", "/").split("/") if p]
    if not parts:
        return False
    if parts[0] in SECRET_DIRS:
        return True
    name = parts[-1]
    if name in SECRET_NAMES or name.endswith(".db"):
        return True
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return True
    return False


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def guess_type(self, path):
        if path.replace("\\", "/").endswith("dashlitefin.html"):
            return "text/html; charset=utf-8"
        return super().guess_type(path)

    def list_directory(self, path):
        self.send_error(404, "Not found")
        return None

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/":
            self.send_response(302)
            self.send_header("Location", "/dashlitefin.html")
            self.end_headers()
            return
        if route == "/api/health":
            _json_bytes({"ok": True, "lab": "ai-4"}, 200, self)
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
        if _is_secret(route):
            self.send_error(404, "Not found")
            return
        return super().do_GET()

    def do_POST(self):
        route = urlparse(self.path).path
        if route == "/api/init-user":
            status, payload = init_user(_bearer(self), _client_ip(self))
            _json_bytes(payload, status, self)
            return
        if route == "/api/ask-lab":
            key = _bearer(self)
            if not llm_ready():
                _json_bytes({"error": "Модель ещё не подключена. Нужен ключ TIMEWEB_AI_KEY на сервере."}, 503, self)
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
    load_env()
    _refresh_weather()
    threading.Thread(target=_weather_loop, name="weather", daemon=True).start()
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"http://{HOST}:{PORT}/dashlitefin.html", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
