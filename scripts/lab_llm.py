"""Вопрос к лаборатории через OpenRouter. Ключ живёт только на сервере."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "deepseek/deepseek-v4-flash"
PROMPT_PATH = ROOT / "docs" / "prompt-ai.md"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TIMEWEB_URL = "https://api.timeweb.ai/v1/chat/completions"
SCREEN_RULES = (
    "\n\n## 5. Вопросы по экрану лаборатории\n"
    "В этой версии нет прогона идей. Поясни карточки из сводки: погода рынка, арена ботов, "
    "сумма в R, как часто до цели, идея вероятности бота.\n"
    "На экране так: вместо сделки и сетапа — вероятность; вместо профита и прибыли — сумма в R; "
    "вместо винрейта — как часто до цели.\n"
    "Не выдумывай цифры вне сводки. Если в сводке нет данных — так и скажи.\n"
    "Картинки и видео не делаешь. Если просят — вежливый отказ: только текст по сводке.\n"
    "Отвечай по-русски, коротко и по-человечески.\n"
)


class _Skip(Exception):
    """Этот способ вызова здесь недоступен, пробуем следующий."""


def system_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8") + SCREEN_RULES
    return SCREEN_RULES.strip()


def load_env() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def _norm_env_name(name: str) -> str:
    return name.upper().replace("-", "_").replace(" ", "_")


def _env_first(*names: str) -> str:
    load_env()
    by_norm = {_norm_env_name(key): value for key, value in os.environ.items()}
    for name in names:
        raw = by_norm.get(_norm_env_name(name)) or ""
        key = raw.strip().strip('"').strip("'")
        if key.lower().startswith("bearer "):
            key = key[7:].strip()
        if key:
            return key
    return ""


def env_key_names() -> list[str]:
    load_env()
    marks = ("TIMEWEB", "OPENROUTER", "AI_KEY", "AI_GATEWAY", "AI_MODEL", "LAB_FOUNDER")
    found = []
    for key in os.environ:
        upper = _norm_env_name(key)
        if any(mark in upper for mark in marks):
            found.append(key)
    return sorted(found)


def api_key() -> str:
    return _env_first("OPENROUTER_API_KEY")


def model_name() -> str:
    return _env_first("OPENROUTER_MODEL") or MODEL


def timeweb_key() -> str:
    return _env_first("TIMEWEB_AI_KEY", "TIMEWEB_AI_GATEWAY_KEY")


def timeweb_model() -> str:
    return _env_first("TIMEWEB_AI_MODEL") or MODEL


def llm_ready() -> bool:
    return bool(timeweb_key() or api_key())


def _clip(text: object, limit: int) -> str:
    value = " ".join(str(text or "").split())
    if len(value) <= limit:
        return value
    return value[: limit - 1] + "…"


def _context_text(context: dict | None) -> str:
    data = context if isinstance(context, dict) else {}
    lines = [
        f"Период сводки: {_clip(data.get('period'), 20) or 'всё время'}",
        f"Сумма в R: {_clip(data.get('sum_r'), 20)}",
        f"Как часто до цели: {_clip(data.get('to_goal'), 20)}%",
        f"Золото: {_clip(data.get('gold'), 180)}",
        f"Серебро: {_clip(data.get('silver'), 180)}",
    ]
    bots = data.get("bots")
    if isinstance(bots, list):
        for bot in bots[:5]:
            if not isinstance(bot, dict):
                continue
            lines.append(
                "Бот "
                + _clip(bot.get("title"), 40)
                + ": "
                + _clip(bot.get("status"), 24)
                + ", "
                + _clip(bot.get("sum_r"), 12)
                + " R, "
                + _clip(bot.get("week"), 8)
                + " в неделю. Идея: "
                + _clip(bot.get("idea"), 160)
            )
    return "\n".join(lines)


def _friendly_http_error(status: int, body: str) -> str:
    low = (body or "").lower()
    if status == 401:
        return "Ключ модели сервер не принял. Проверь TIMEWEB_AI_KEY или OPENROUTER_API_KEY в переменных приложения."
    if status == 402:
        return "На ключе модели нет доступного баланса."
    if status == 403 and "security policy" in low:
        return "Сеть сервера не пустила запрос к модели. Это не ключ — канал режут по дороге."
    if status == 404:
        return "Такой модели нет. Проверь OPENROUTER_MODEL."
    snippet = " ".join((body or "").split())[:160]
    if snippet:
        return "Модель не ответила. " + snippet
    return "Модель не ответила."


def ask_lab(question: str, context: dict | None = None) -> str:
    if not llm_ready():
        raise RuntimeError("Ключ модели ещё не лежит на сервере. На Timeweb нужен TIMEWEB_AI_KEY.")
    q = _clip(question, 500)
    if not q:
        raise RuntimeError("Пустой вопрос.")
    use_timeweb = bool(timeweb_key())
    payload = {
        "model": timeweb_model() if use_timeweb else model_name(),
        "temperature": 0.4,
        "max_tokens": 500,
        "messages": [
            {"role": "system", "content": system_prompt()},
            {
                "role": "user",
                "content": "Сводка на экране:\n" + _context_text(context) + "\n\nВопрос: " + q,
            },
        ],
    }
    body = _via_timeweb(payload) if use_timeweb else _openrouter_chat(payload)
    if isinstance(body, dict) and body.get("error"):
        err = body["error"]
        msg = err.get("message") if isinstance(err, dict) else str(err)
        raise RuntimeError(_friendly_http_error(0, str(msg)))
    choices = body.get("choices") if isinstance(body, dict) else None
    if not choices:
        raise RuntimeError("Пустой ответ модели.")
    message = (choices[0] or {}).get("message") or {}
    text = (message.get("content") or "").strip()
    if not text:
        raise RuntimeError("Модель вернула пустой текст.")
    return text


def _via_timeweb(payload: dict) -> dict:
    key = timeweb_key()
    if not key:
        raise _Skip()
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(TIMEWEB_URL, data=body, method="POST", headers=_headers(key))
    try:
        with urllib.request.urlopen(req, timeout=50) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(_friendly_http_error(err.code, detail)) from err
    except urllib.error.URLError as err:
        raise RuntimeError("Модель Timeweb недоступна.") from err


def _headers(key: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json; charset=utf-8",
        "X-Title": "Yasno.trade",
        "HTTP-Referer": "https://yasnotrade.ru",
        "User-Agent": "YasnoLab/1.0",
        "Accept": "application/json",
    }


def _via_powershell(payload: dict) -> dict:
    if os.name != "nt":
        raise _Skip()
    key = api_key()
    work = Path(tempfile.mkdtemp(prefix="yasno_or_"))
    payload_path = work / "in.json"
    out_path = work / "out.json"
    script_path = work / "call.ps1"
    payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    script = f"""
$ErrorActionPreference = "Stop"
$key = $env:OPENROUTER_API_KEY
if (-not $key) {{ throw "NO_KEY" }}
$wc = New-Object System.Net.WebClient
$wc.Encoding = [System.Text.Encoding]::UTF8
$wc.Headers["Authorization"] = "Bearer $key"
$wc.Headers["Content-Type"] = "application/json; charset=utf-8"
$wc.Headers["X-Title"] = "Yasno.trade"
$wc.Headers["HTTP-Referer"] = "https://yasnotrade.ru"
$inBytes = [System.IO.File]::ReadAllBytes({json.dumps(str(payload_path))})
$outBytes = $wc.UploadData({json.dumps(OPENROUTER_URL)}, "POST", $inBytes)
[System.IO.File]::WriteAllBytes({json.dumps(str(out_path))}, $outBytes)
"""
    script_path.write_text(script, encoding="utf-8")
    env = os.environ.copy()
    env["OPENROUTER_API_KEY"] = key
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
            capture_output=True,
            text=True,
            timeout=50,
            env=env,
        )
        if proc.returncode != 0 or not out_path.exists():
            err = (proc.stderr or proc.stdout or "нет ответа").strip()[:240]
            raise RuntimeError("Модель не ответила. " + err)
        return json.loads(out_path.read_text(encoding="utf-8-sig"))
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _via_curl_cffi(payload: dict) -> dict:
    try:
        from curl_cffi import requests as cf_requests
    except ImportError as err:
        raise _Skip() from err
    key = api_key()
    last_error = "Модель не ответила."
    for impersonate in ("chrome", "chrome131", "safari18_0"):
        try:
            resp = cf_requests.post(
                OPENROUTER_URL,
                headers=_headers(key),
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                timeout=50,
                impersonate=impersonate,
            )
        except Exception as err:
            last_error = "Модель недоступна."
            print("openrouter curl_cffi", impersonate, type(err).__name__, file=sys.stderr, flush=True)
            continue
        if resp.status_code >= 400:
            last_error = _friendly_http_error(resp.status_code, resp.text)
            print("openrouter curl_cffi", impersonate, resp.status_code, file=sys.stderr, flush=True)
            if resp.status_code != 403:
                raise RuntimeError(last_error)
            continue
        return resp.json()
    raise RuntimeError(last_error)


def _via_urllib(payload: dict) -> dict:
    key = api_key()
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(OPENROUTER_URL, data=body, method="POST", headers=_headers(key))
    try:
        with urllib.request.urlopen(req, timeout=50) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(_friendly_http_error(err.code, detail)) from err
    except urllib.error.URLError as err:
        raise RuntimeError("Модель недоступна.") from err


def _via_tls_client(payload: dict) -> dict:
    try:
        import tls_client
    except ImportError as err:
        raise _Skip() from err
    key = api_key()
    last_error = "Модель не ответила."
    for ident in ("chrome_120", "chrome112", "firefox_120"):
        try:
            session = tls_client.Session(client_identifier=ident, random_tls_extension_order=True)
            resp = session.post(
                OPENROUTER_URL,
                headers=_headers(key),
                json=payload,
                timeout_seconds=50,
            )
        except Exception as err:
            print("openrouter tls_client", ident, type(err).__name__, file=sys.stderr, flush=True)
            last_error = "Модель недоступна."
            continue
        status = int(getattr(resp, "status_code", 0) or 0)
        text = getattr(resp, "text", "") or ""
        if status >= 400:
            last_error = _friendly_http_error(status, text)
            print("openrouter tls_client", ident, status, file=sys.stderr, flush=True)
            if status != 403:
                raise RuntimeError(last_error)
            continue
        data = resp.json()
        return data if isinstance(data, dict) else json.loads(text)
    raise RuntimeError(last_error)


def _openrouter_chat(payload: dict) -> dict:
    last = "Модель недоступна."
    for sender in (_via_powershell, _via_tls_client, _via_curl_cffi, _via_urllib):
        try:
            return sender(payload)
        except _Skip:
            continue
        except RuntimeError as err:
            last = str(err)
            continue
    raise RuntimeError(last)
