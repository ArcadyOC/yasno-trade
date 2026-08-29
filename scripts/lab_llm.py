"""Вопрос к лаборатории через OpenRouter. Ключ живёт только на сервере."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "deepseek/deepseek-v4-flash"
PROMPT_PATH = ROOT / "docs" / "prompt-ai.md"
SCREEN_RULES = (
    "\n\n## 5. Вопросы по экрану лаборатории\n"
    "Если вопрос не про отчёт прогона, поясни карточки из сводки: погода рынка, арена ботов, "
    "сумма в R, как часто до цели, идея вероятности бота.\n"
    "На экране так: вместо сделки и сетапа — вероятность; вместо профита и прибыли — сумма в R "
    "или итог прогона; вместо винрейта — как часто до цели.\n"
    "Не выдумывай цифры вне сводки. Если в сводке нет данных — так и скажи.\n"
    "Картинки и видео не делаешь. Если просят — вежливый отказ: только текст по сводке.\n"
    "Отвечай по-русски, коротко и по-человечески. Правила из разделов 1–4 этого промпта важнее всего.\n"
)


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


def api_key() -> str:
    load_env()
    return (os.environ.get("OPENROUTER_API_KEY") or "").strip()


def model_name() -> str:
    load_env()
    return (os.environ.get("OPENROUTER_MODEL") or MODEL).strip()


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


def ask_lab(question: str, context: dict | None = None) -> str:
    key = api_key()
    if not key:
        raise RuntimeError("Ключ модели ещё не лежит на сервере.")
    q = _clip(question, 500)
    if not q:
        raise RuntimeError("Пустой вопрос.")
    payload = {
        "model": model_name(),
        "temperature": 0.4,
        "max_tokens": 500,
        "reasoning": {"exclude": True},
        "messages": [
            {"role": "system", "content": system_prompt()},
            {
                "role": "user",
                "content": "Сводка на экране:\n" + _context_text(context) + "\n\nВопрос: " + q,
            },
        ],
    }
    body = _openrouter_chat(payload)
    choices = body.get("choices") if isinstance(body, dict) else None
    if not choices:
        raise RuntimeError("Пустой ответ модели.")
    message = (choices[0] or {}).get("message") or {}
    text = (message.get("content") or "").strip()
    if not text:
        raise RuntimeError("Модель вернула пустой текст.")
    return text


def _openrouter_chat(payload: dict) -> dict:
    work = Path(tempfile.mkdtemp(prefix="yasno_or_"))
    payload_path = work / "in.json"
    out_path = work / "out.json"
    script_path = work / "call.ps1"
    payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    script = f"""
$ErrorActionPreference = "Stop"
$root = {json.dumps(str(ROOT))}
$key = $null
Get-Content -Encoding UTF8 (Join-Path $root ".env") | ForEach-Object {{
  if ($_ -match "^OPENROUTER_API_KEY=(.*)$") {{ $key = $Matches[1].Trim().Trim('"') }}
}}
if (-not $key) {{ throw "NO_KEY" }}
$wc = New-Object System.Net.WebClient
$wc.Encoding = [System.Text.Encoding]::UTF8
$wc.Headers["Authorization"] = "Bearer $key"
$wc.Headers["Content-Type"] = "application/json; charset=utf-8"
$wc.Headers["X-Title"] = "Yasno.trade"
$wc.Headers["HTTP-Referer"] = "https://yasno.trade"
$inBytes = [System.IO.File]::ReadAllBytes({json.dumps(str(payload_path))})
$outBytes = $wc.UploadData("https://openrouter.ai/api/v1/chat/completions", "POST", $inBytes)
[System.IO.File]::WriteAllBytes({json.dumps(str(out_path))}, $outBytes)
"""
    script_path.write_text(script, encoding="utf-8")
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
            capture_output=True,
            text=True,
            timeout=50,
        )
        if proc.returncode != 0 or not out_path.exists():
            err = (proc.stderr or proc.stdout or "нет ответа").strip()[:240]
            raise RuntimeError("Модель не ответила. " + err)
        return json.loads(out_path.read_text(encoding="utf-8-sig"))
    finally:
        shutil.rmtree(work, ignore_errors=True)
