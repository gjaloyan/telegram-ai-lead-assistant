from __future__ import annotations

import csv
from pathlib import Path
from datetime import datetime, timezone


FIELDS = [
    "timestamp_utc",
    "chat_id",
    "raw_text",
    "category",
    "intent",
    "name",
    "phone",
]


def append_lead(path: str, row: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    file_exists = p.exists()
    with p.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in FIELDS})


def count_rows(path: str) -> int:
    p = Path(path)
    if not p.exists():
        return 0
    with p.open("r", encoding="utf-8") as f:
        return max(sum(1 for _ in f) - 1, 0)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
