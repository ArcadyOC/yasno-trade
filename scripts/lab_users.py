"""Ключ исследователя: выдача пропуска и поиск профиля."""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "lab_users.db"
START_ENERGY = 100
START_RANK = 1
TEST_COST = 5


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
    conn.commit()
    return conn


def _row(user) -> dict:
    return {
        "user_key": user["user_key"],
        "nickname": user["nickname"],
        "energy": user["energy_balance"],
        "energy_max": START_ENERGY,
        "rank": user["rank"],
        "rank_label": "Стажёр" if user["rank"] == 1 else f"Ранг {user['rank']}",
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
        return 201, {
            "user_key": key,
            "nickname": nick,
            "energy": START_ENERGY,
            "energy_max": START_ENERGY,
            "rank": START_RANK,
            "rank_label": "Стажёр",
            "created": True,
        }
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
        nxt = int(row["energy_balance"]) + delta
        if delta < 0 and int(row["energy_balance"]) < abs(delta):
            return 403, {
                "error": "Мало энергии для проверки. Нужно 5 единиц.",
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
