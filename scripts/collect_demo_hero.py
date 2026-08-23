"""Сводка трёх верхних карточек dashlitefin из пяти демо-ботов kvant_lab."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

KVANT_LAB = Path(r"C:\Users\pushi\Desktop\kvant_lab")
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "lab_hero.json"
ONLINE_MAX_AGE = timedelta(hours=2)
STALE_AFTER = timedelta(days=10)

BOT_FACES = {
    "xau-trend": {"title": "Золото · тренд", "metal": "Золото"},
    "xag-trend": {"title": "Серебро · тренд", "metal": "Серебро"},
    "planner": {"title": "Оба металла · цепочка", "metal": "Золото и серебро"},
    "idea-004-observe": {"title": "Серебро · наблюдение", "metal": "Серебро"},
    "mv-m5-impulse": {"title": "Серебро · импульс", "metal": "Серебро"},
}


def _num(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_dt(value):
    if not value:
        return None
    text = str(value).strip().replace("Z", "")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:19] if len(text) >= 19 and "T" in text else text[:19], fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text[:19])
    except ValueError:
        return None


def _risk(trade: dict) -> float | None:
    details = trade.get("details") or {}
    sl_usd = _num(details.get("sl_usd"))
    if sl_usd and sl_usd > 0:
        return abs(sl_usd)
    sl = _num(trade.get("sl") or trade.get("sl_price") or details.get("sl_price"))
    entry = _num(trade.get("entry_price"))
    if sl is not None and entry is not None:
        risk = abs(entry - sl)
        if risk > 1e-9:
            return risk
    return None


def _r_multiple(trade: dict) -> float | None:
    pnl = _num(trade.get("pnl"))
    risk = _risk(trade)
    if pnl is None or risk is None:
        return None
    return pnl / risk


def _is_closed(trade: dict) -> bool:
    status = str(trade.get("status") or "").lower()
    if status:
        return status == "closed"
    return trade.get("pnl") is not None and trade.get("exit_time")


def _is_win(trade: dict, r_value: float) -> bool:
    result = str(trade.get("result") or trade.get("exit_reason") or "").lower()
    if result in {"win", "take", "tp"}:
        return True
    if result in {"loss", "stop", "sl"}:
        return False
    return r_value > 0


def _load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_closed(name: str, payload: dict):
    items = payload.get("trades") or payload.get("setups") or []
    for trade in items:
        if not _is_closed(trade):
            continue
        r_value = _r_multiple(trade)
        if r_value is None:
            continue
        exit_at = _parse_dt(trade.get("exit_time") or trade.get("logged_at"))
        symbol = str(trade.get("symbol") or "")
        if not symbol and "xag" in name:
            symbol = "XAGUSD"
        elif not symbol and "xau" in name:
            symbol = "XAUUSD"
        yield {
            "bot": name,
            "r": r_value,
            "win": _is_win(trade, r_value),
            "exit_at": exit_at,
            "symbol": symbol or "—",
        }


def _fresh(path: Path, payload: dict, now: datetime) -> bool:
    stamps = [
        payload.get("updated_at"),
        payload.get("last_check"),
        payload.get("last_mt5_ok_at"),
        payload.get("last_checked_bar"),
    ]
    for stamp in stamps:
        parsed = _parse_dt(stamp)
        if parsed and now - parsed <= ONLINE_MAX_AGE:
            return True
    if path.exists() and now - datetime.fromtimestamp(path.stat().st_mtime) <= ONLINE_MAX_AGE:
        return True
    return False


def _monitor_online() -> set[str]:
    status = KVANT_LAB / "bot_supervisor" / "logs" / "monitor_last_status.txt"
    if not status.exists():
        return set()
    text = status.read_text(encoding="utf-8", errors="replace")
    header = re.search(r"time=(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", text)
    if header:
        parsed = _parse_dt(header.group(1))
        if parsed and datetime.now() - parsed > ONLINE_MAX_AGE:
            return set()
    found = set()
    for match in re.finditer(r"bot (\S+) -> (\d+)", text):
        name, pid = match.group(1), match.group(2)
        if pid != "0":
            found.add(name)
    return found


def _sparkline(points: list[float]) -> dict:
    if not points:
        return {"line": "M5,15 L95,15", "area": "M5,15 L95,15 L95,30 L5,30 Z", "positive": True}
    ymin, ymax = min(points), max(points)
    span = ymax - ymin or 1.0
    coords = []
    for i, value in enumerate(points):
        x = 5 + (90 * i / max(len(points) - 1, 1))
        y = 26 - ((value - ymin) / span) * 22
        coords.append((x, y))
    line = "M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    last_x, last_y = coords[-1]
    area = f"{line} L{last_x:.1f},30 L5,30 Z"
    return {"line": line, "area": area, "positive": points[-1] >= 0}


def _period_stats(closed: list[dict], start: datetime | None) -> dict:
    subset = [row for row in closed if start is None or (row["exit_at"] and row["exit_at"] >= start)]
    n = len(subset)
    wins = sum(1 for row in subset if row["win"])
    total_r = sum(row["r"] for row in subset)
    times = [row["exit_at"] for row in subset if row["exit_at"]]
    if len(times) >= 2:
        span_days = max((max(times) - min(times)).days, 1)
        trades_per_week = n / (span_days / 7)
    else:
        trades_per_week = float(n)
    ordered = [row["r"] for row in sorted(subset, key=lambda x: x["exit_at"] or datetime.min)]
    cumulative = []
    acc = 0.0
    for value in ordered[-24:]:
        acc += value
        cumulative.append(acc)
    return {
        "closed": n,
        "wins": wins,
        "win_rate_pct": round(100 * wins / n, 1) if n else 0.0,
        "sum_r": round(total_r, 1),
        "trades_per_week": round(trades_per_week, 1),
        "sparkline": _sparkline(cumulative),
    }


def collect() -> dict:
    now = datetime.now()
    bots_cfg = _load_json(KVANT_LAB / "bot_supervisor" / "bots.json") or []
    monitor_online = _monitor_online()

    sources = {
        "xau-trend": KVANT_LAB / "demo_bots" / "xauusd" / "data" / "live_stats.json",
        "xag-trend": KVANT_LAB / "demo_bots" / "xagusd" / "trend-silver" / "current" / "data" / "live_stats.json",
        "planner": KVANT_LAB / "demo_bots" / "planner" / "bot" / "data" / "live_stats.json",
        "idea-004-observe": KVANT_LAB / "demo_bots" / "xagusd" / "idea_004_observe" / "data" / "bot_state.json",
        "mv-m5-impulse": KVANT_LAB / "demo_bots" / "xagusd" / "mv_m5_impulse" / "data" / "bot_state.json",
    }
    extra_fresh = {
        "xau-trend": KVANT_LAB / "demo_bots" / "xauusd" / "data" / "bot_state.json",
        "xag-trend": KVANT_LAB / "demo_bots" / "xagusd" / "trend-silver" / "current" / "data" / "bot_state_xagusd.json",
        "planner": KVANT_LAB / "demo_bots" / "planner" / "bot" / "state.json",
    }

    closed: list[dict] = []
    per_bot = []
    online = 0
    configured = [item["name"] for item in bots_cfg] or list(sources)

    for name in configured:
        path = sources.get(name)
        payload = _load_json(path) if path else None
        bot_closed = list(_iter_closed(name, payload or {}))
        closed.extend(bot_closed)
        is_online = name in monitor_online
        if not is_online and payload and path:
            is_online = _fresh(path, payload, now)
        extra = extra_fresh.get(name)
        if not is_online and extra:
            extra_payload = _load_json(extra) or {}
            is_online = _fresh(extra, extra_payload, now)
        if is_online:
            online += 1
        bot_r = sum(row["r"] for row in bot_closed)
        bot_wins = sum(1 for row in bot_closed if row["win"])
        n = len(bot_closed)
        ordered = sorted(bot_closed, key=lambda x: x["exit_at"] or datetime.min)
        last_exit = ordered[-1]["exit_at"] if ordered else None
        week_closed = [row for row in bot_closed if row["exit_at"] and row["exit_at"] >= now - timedelta(days=7)]
        times = [row["exit_at"] for row in bot_closed if row["exit_at"]]
        if len(times) >= 2:
            span_days = max((max(times) - min(times)).days, 1)
            trades_per_week = n / (span_days / 7)
        else:
            trades_per_week = float(n)
        stale = bool(last_exit and now - last_exit > STALE_AFTER)
        if not is_online:
            status, status_label, footnote = "offline", "Нет связи", "Процесс сейчас не отвечает"
        elif n == 0:
            status, status_label, footnote = "wait", "Ждёт", "Пока нет закрытых"
        elif stale:
            status, status_label, footnote = "stale", "Давно без закрытий", "Последнее закрытие больше 10 дней назад"
        else:
            status, status_label, footnote = (
                "live",
                "В работе",
                f"{n} закрытых · {trades_per_week:.1f} в неделю",
            )
        acc, spark_pts = 0.0, []
        for row in ordered:
            acc += row["r"]
            spark_pts.append(acc)
        spark_pts = spark_pts[-16:]
        recent = []
        for row in reversed(ordered[-3:]):
            metal = (
                "Золото"
                if "XAU" in row["symbol"]
                else "Серебро"
                if "XAG" in row["symbol"]
                else BOT_FACES.get(name, {}).get("metal", "")
            )
            recent.append(
                {
                    "label": metal or row["symbol"],
                    "r": round(row["r"], 1),
                    "when": row["exit_at"].strftime("%d.%m %H:%M") if row["exit_at"] else "",
                }
            )
        face = BOT_FACES.get(name, {"title": name, "metal": ""})
        per_bot.append(
            {
                "id": name,
                "name": name,
                "title": face["title"],
                "metal": face["metal"],
                "online": is_online,
                "status": status,
                "status_label": status_label,
                "footnote": footnote,
                "closed": n,
                "wins": bot_wins,
                "sum_r": round(bot_r, 1),
                "week_r": round(sum(row["r"] for row in week_closed), 1),
                "win_rate_pct": round(100 * bot_wins / n, 1) if n else None,
                "trades_per_week": round(trades_per_week, 1),
                "sparkline": _sparkline(spark_pts),
                "recent": recent,
                "last_exit": last_exit.strftime("%d.%m %H:%M") if last_exit else None,
            }
        )

    per_bot.sort(key=lambda bot: (bot["sum_r"], bot["closed"]), reverse=True)

    all_stats = _period_stats(closed, None)
    month_stats = _period_stats(closed, now - timedelta(days=30))
    week_stats = _period_stats(closed, now - timedelta(days=7))

    week_r = week_stats["sum_r"]
    month_r = month_stats["sum_r"]
    if week_r > 0 and (month_r <= 0 or week_r >= month_r / 4):
        caption = "Высокий темп прироста"
        caption_tone = "up"
    elif week_r > 0:
        caption = "Плюс за неделю"
        caption_tone = "up"
    elif week_r < 0:
        caption = "Минус за неделю"
        caption_tone = "down"
    else:
        caption = "Нет закрытых за неделю"
        caption_tone = "flat"

    return {
        "updated_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": str(KVANT_LAB / "demo_bots"),
        "profit": {
            "all": all_stats["sum_r"],
            "month": month_stats["sum_r"],
            "week": week_stats["sum_r"],
            "caption": caption,
            "caption_tone": caption_tone,
            "sparkline": {
                "all": all_stats["sparkline"],
                "month": month_stats["sparkline"],
                "week": week_stats["sparkline"],
            },
        },
        "realization": {
            "all": all_stats["win_rate_pct"],
            "month": month_stats["win_rate_pct"],
            "week": week_stats["win_rate_pct"],
            "closed_all": all_stats["closed"],
            "wins_all": all_stats["wins"],
            "label": "Как часто до цели",
        },
        "agents": {
            "online": online,
            "total": len(configured),
            "label": "Системы онлайн" if online == len(configured) else "Часть систем онлайн",
        },
        "activity": {
            "trades_per_week_all": all_stats["trades_per_week"],
            "trades_per_week_month": month_stats["trades_per_week"],
            "trades_week_count": week_stats["closed"],
        },
        "bots": per_bot,
    }


def main():
    snapshot = collect()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    print(
        f"R all/month/week: {snapshot['profit']['all']} / "
        f"{snapshot['profit']['month']} / {snapshot['profit']['week']}"
    )
    print(
        f"WR {snapshot['realization']['all']}%  "
        f"agents {snapshot['agents']['online']}/{snapshot['agents']['total']}  "
        f"в неделю {snapshot['activity']['trades_per_week_all']}"
    )
    for bot in snapshot["bots"]:
        print(
            f"  {bot['title']}: {bot['sum_r']} R  {bot['status_label']}  "
            f"{bot['closed']} закр.  {bot['trades_per_week']}/нед"
        )


if __name__ == "__main__":
    main()
