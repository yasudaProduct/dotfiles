#!/usr/bin/env python3
"""Claude Code statusLine → RunCat Neo custom metrics JSON.

Register in ~/.claude/settings.json:

  {
    "statusLine": {
      "type": "command",
      "command": "/Users/yuta/.runcat/update-claude-metrics.py"
    }
  }

Writes ~/.runcat/claude.json (override with RUNCAT_OUT_FILE).
Prints a short status line to stdout for the Claude Code TUI.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HOME = Path.home()
SESSIONS_DIR = HOME / ".claude" / "sessions"
OUT = Path(
    os.environ.get("RUNCAT_OUT_FILE", str(HOME / ".runcat" / "claude.json"))
)
MISSING = "—"


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def active_session_count() -> int:
    if not SESSIONS_DIR.is_dir():
        return 0
    count = 0
    for path in SESSIONS_DIR.glob("*.json"):
        try:
            with path.open() as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        pid = data.get("pid")
        if isinstance(pid, int) and pid_alive(pid):
            count += 1
    return count


def format_pct(value: Any) -> str | None:
    if value is None:
        return None
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    # Drop trailing .0 for whole numbers (67.0 → 67%)
    text = f"{n:g}"
    return f"{text}%"


def format_reset(resets_at: Any) -> str | None:
    if resets_at is None:
        return None
    try:
        ts = int(resets_at)
    except (TypeError, ValueError):
        return None
    local = datetime.fromtimestamp(ts).astimezone()
    return local.strftime("%H:%M")


def rate_row(title: str, window: dict[str, Any] | None) -> dict[str, Any]:
    window = window or {}
    pct_text = format_pct(window.get("used_percentage"))
    reset = format_reset(window.get("resets_at"))
    if pct_text is None:
        return {"title": title, "formattedValue": MISSING}
    formatted = f"{pct_text} · {reset}" if reset else pct_text
    try:
        normalized = round(float(window["used_percentage"]) / 100, 4)
    except (TypeError, ValueError, KeyError):
        return {"title": title, "formattedValue": formatted}
    return {
        "title": title,
        "formattedValue": formatted,
        "normalizedValue": max(0.0, min(1.0, normalized)),
    }


def context_row(used_percentage: Any) -> dict[str, Any]:
    pct_text = format_pct(used_percentage)
    if pct_text is None:
        return {"title": "コンテキスト", "formattedValue": MISSING}
    try:
        normalized = round(float(used_percentage) / 100, 4)
    except (TypeError, ValueError):
        return {"title": "コンテキスト", "formattedValue": pct_text}
    return {
        "title": "コンテキスト",
        "formattedValue": pct_text,
        "normalizedValue": max(0.0, min(1.0, normalized)),
    }


def read_stdin_payload() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        payload = json.loads(raw)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def build_snapshot(payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
    model = (payload.get("model") or {}).get("display_name") or MISSING
    ctx = (payload.get("context_window") or {}).get("used_percentage")
    rate_limits = payload.get("rate_limits") or {}
    five = rate_limits.get("five_hour") if isinstance(rate_limits, dict) else None
    seven = rate_limits.get("seven_day") if isinstance(rate_limits, dict) else None
    if not isinstance(five, dict):
        five = None
    if not isinstance(seven, dict):
        seven = None

    five_row = rate_row("5時間", five)
    seven_row = rate_row("7日", seven)
    ctx_row = context_row(ctx)
    active = active_session_count()

    five_pct = format_pct((five or {}).get("used_percentage"))
    ctx_pct = format_pct(ctx)
    bar = five_pct or ctx_pct or MISSING

    snapshot: dict[str, Any] = {
        "title": "Claude Code",
        "symbol": "brain.head.profile",
        "metricsBarValue": bar,
        "metrics": [
            {"title": "モデル", "formattedValue": model},
            ctx_row,
            five_row,
            seven_row,
            {"title": "アクティブ", "formattedValue": str(active)},
        ],
        "lastUpdatedDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Compact status line for Claude Code TUI
    parts = [model]
    if ctx_pct:
        parts.append(f"コンテキスト {ctx_pct}")
    if five_pct:
        parts.append(f"5h {five_pct}")
    status_line = " · ".join(parts)
    return snapshot, status_line


def write_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".runcat-", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def main() -> None:
    payload = read_stdin_payload()
    snapshot, status_line = build_snapshot(payload)
    write_atomic(OUT, snapshot)
    print(status_line)


if __name__ == "__main__":
    main()
