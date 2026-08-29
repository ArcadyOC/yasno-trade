"""Ключ исследователя: выдача пропуска и поиск профиля."""

from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "lab_users.db"
START_ENERGY = 100
START_RANK = 1
TRAINEE_COST = 10
RESEARCHER_COST = 5
ACTION_COST = TRAINEE_COST
TEST_COST = ACTION_COST
FOUNDER_TITLE = "Основатель"
TRAINEE_TITLE = "Стажёр"
RESEARCHER_TITLE = "Исследователь"
PRO_TITLE = "Профи"
PRO_STARS = 3


def founder_key() -> str:
    pinned = (os.environ.get("LAB_FOUNDER_KEY") or "").strip()
    if pinned:
        return pinned
    path = ROOT / ".env"
    if not path.exists():
        return ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == "LAB_FOUNDER_KEY":
            return value.strip().strip('"').strip("'")
    return ""


def is_founder(user_key: str | None) -> bool:
    pinned = founder_key()
    return bool(pinned and user_key and user_key == pinned)


def _stars(user) -> int:
    try:
        return max(0, min(PRO_STARS, int(user["stars"])))
    except (KeyError, IndexError, TypeError, ValueError):
        return 0


def _ladder(stars: int) -> tuple[str, str]:
    if stars >= PRO_STARS:
        return "pro", PRO_TITLE
    if stars >= 1:
        return "researcher", RESEARCHER_TITLE
    return "trainee", TRAINEE_TITLE


def _role_for(user_key: str, stars: int = 0) -> tuple[str, str]:
    if is_founder(user_key):
        return "founder", FOUNDER_TITLE
    return _ladder(stars)


def energy_locked(user_key: str | None, stars: int = 0) -> bool:
    return is_founder(user_key) or stars >= PRO_STARS


def _action_cost(user_key: str, stars: int) -> int:
    if energy_locked(user_key, stars):
        return 0
    if stars >= 1:
        return RESEARCHER_COST
    return TRAINEE_COST


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_key TEXT PRIMARY KEY,
            nickname TEXT NOT NULL,
            energy_balance INTEGER NOT NULL,
            rank INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            ip_hash TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS hypothesis_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_key TEXT NOT NULL,
            nickname TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cols = {info[1] for info in conn.execute("PRAGMA table_info(users)")}
    if "stars" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN stars INTEGER NOT NULL DEFAULT 0")
    conn.commit()
    return conn


def _row(user) -> dict:
    stars = _stars(user)
    role, role_label = _role_for(user["user_key"], stars)
    locked = energy_locked(user["user_key"], stars)
    return {
        "user_key": user["user_key"],
        "nickname": user["nickname"],
        "energy": START_ENERGY if locked else user["energy_balance"],
        "energy_max": START_ENERGY,
        "energy_locked": locked,
        "stars": stars,
        "action_cost": _action_cost(user["user_key"], stars),
        "rank": user["rank"],
        "rank_label": role_label,
        "role": role,
        "role_label": role_label,
        "created": bool(user["created_at"]),
    }


def hash_ip(ip: str | None) -> str:
    raw = (ip or "unknown").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _new_key() -> str:
    return "yasno_" + secrets.token_hex(6)


def _new_nick(conn: sqlite3.Connection) -> str:
    for _ in range(20):
        nick = f"Lab_{secrets.randbelow(9000) + 1000}"
        exists = conn.execute("SELECT 1 FROM users WHERE nickname = ?", (nick,)).fetchone()
        if not exists:
            return nick
    return f"Lab_{secrets.token_hex(3)}"


def find_user(user_key: str | None) -> dict | None:
    if not user_key:
        return None
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM users WHERE user_key = ?", (user_key,)).fetchone()
        return _row(row) if row else None
    finally:
        conn.close()


def find_user_by_ip(ip: str | None) -> dict | None:
    ip_hash = hash_ip(ip)
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE ip_hash = ? ORDER BY created_at ASC LIMIT 1",
            (ip_hash,),
        ).fetchone()
        return _row(row) if row else None
    finally:
        conn.close()


def init_user(existing_key: str | None, ip: str | None) -> tuple[int, dict]:
    found = find_user(existing_key)
    if found:
        return 200, found

    if is_founder(existing_key):
        conn = _connect()
        try:
            now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            conn.execute(
                """
                INSERT INTO users (user_key, nickname, energy_balance, rank, created_at, ip_hash)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (existing_key, "Маша", START_ENERGY, START_RANK, now, hash_ip(ip)),
            )
            conn.commit()
            fresh = conn.execute("SELECT * FROM users WHERE user_key = ?", (existing_key,)).fetchone()
            payload = _row(fresh)
            payload["created"] = True
            return 201, payload
        finally:
            conn.close()

    by_ip = find_user_by_ip(ip)
    if by_ip:
        return 200, by_ip

    ip_hash = hash_ip(ip)
    conn = _connect()
    try:
        key = _new_key()
        nick = _new_nick(conn)
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        conn.execute(
            """
            INSERT INTO users (user_key, nickname, energy_balance, rank, created_at, ip_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (key, nick, START_ENERGY, START_RANK, now, ip_hash),
        )
        conn.commit()
        fresh = conn.execute("SELECT * FROM users WHERE user_key = ?", (key,)).fetchone()
        payload = _row(fresh)
        payload["created"] = True
        return 201, payload
    finally:
        conn.close()


def change_energy(user_key: str | None, delta: int) -> tuple[int, dict]:
    user = find_user(user_key)
    if not user:
        return 401, {"error": "Нет такого пропуска. Открой страницу заново или вставь ключ."}
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM users WHERE user_key = ?", (user_key,)).fetchone()
        if not row:
            return 401, {"error": "Нет такого пропуска. Открой страницу заново или вставь ключ."}
        stars = _stars(row)
        cost = _action_cost(user_key, stars)
        if energy_locked(user_key, stars) or delta == 0:
            if energy_locked(user_key, stars) and int(row["energy_balance"]) != START_ENERGY:
                conn.execute(
                    "UPDATE users SET energy_balance = ? WHERE user_key = ?",
                    (START_ENERGY, user_key),
                )
                conn.commit()
            fresh = conn.execute("SELECT * FROM users WHERE user_key = ?", (user_key,)).fetchone()
            return 200, _row(fresh)
        nxt = int(row["energy_balance"]) + delta
        if delta < 0 and int(row["energy_balance"]) < abs(delta):
            need = cost if cost else abs(delta)
            return 403, {
                "error": f"Мало энергии. Нужно {need} единиц на любой ответ.",
                **_row(row),
            }
        conn.execute("UPDATE users SET energy_balance = ? WHERE user_key = ?", (nxt, user_key))
        conn.commit()
        fresh = conn.execute("SELECT * FROM users WHERE user_key = ?", (user_key,)).fetchone()
        return 200, _row(fresh)
    finally:
        conn.close()


def set_nickname(user_key: str | None, nickname: str) -> tuple[int, dict]:
    user = find_user(user_key)
    if not user:
        return 401, {"error": "Нет такого пропуска. Открой страницу заново или вставь ключ."}
    nick = " ".join((nickname or "").split())
    if len(nick) < 2 or len(nick) > 24:
        return 400, {"error": "Имя — от 2 до 24 знаков."}
    conn = _connect()
    try:
        taken = conn.execute(
            "SELECT 1 FROM users WHERE nickname = ? AND user_key != ?",
            (nick, user_key),
        ).fetchone()
        if taken:
            return 409, {"error": "Такое имя уже занято."}
        conn.execute("UPDATE users SET nickname = ? WHERE user_key = ?", (nick, user_key))
        conn.commit()
        fresh = conn.execute("SELECT * FROM users WHERE user_key = ?", (user_key,)).fetchone()
        return 200, _row(fresh)
    finally:
        conn.close()


def log_hypothesis_run(user_key: str, nickname: str, title: str) -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO hypothesis_runs (user_key, nickname, title, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_key, nickname, title, datetime.now().strftime("%Y-%m-%dT%H:%M:%S")),
        )
        conn.commit()
    finally:
        conn.close()


def lab_pulse() -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    conn = _connect()
    try:
        today_n = conn.execute(
            "SELECT COUNT(*) AS n FROM hypothesis_runs WHERE created_at LIKE ?",
            (today + "%",),
        ).fetchone()["n"]
        all_n = conn.execute("SELECT COUNT(*) AS n FROM hypothesis_runs").fetchone()["n"]
        last = conn.execute(
            "SELECT nickname, title, created_at FROM hypothesis_runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()
    last_run = None
    if last:
        last_run = {
            "nickname": last["nickname"],
            "title": last["title"],
            "created_at": last["created_at"],
        }
    return {"today": today_n, "all": all_n, "last": last_run}
