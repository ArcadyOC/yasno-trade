"""Вопрос к лаборатории через OpenRouter. Ключ живёт только на сервере."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "deepseek/deepseek-v4-flash"
PROMPT_PATH = ROOT / "docs" / "prompt-ai.md"
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
    key = api_key()
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        method="POST",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json; charset=utf-8",
            "X-Title": "Yasno.trade",
            "HTTP-Referer": "https://yasnotrade.ru",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=50) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")[:240]
        raise RuntimeError("Модель не ответила. " + detail) from err
    except urllib.error.URLError as err:
        raise RuntimeError("Модель недоступна.") from err
