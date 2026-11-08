"""Beta storage: a 4-debates-per-month cap per school, and the human judges' corrections.

Uses local JSON files. On Streamlit Community Cloud these reset whenever the
app restarts, which is fine for a beta. In production this would move to a
database such as Supabase.
"""
import json
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
LIMIT = 4


def _usage() -> dict:
    p = DATA / "usage.json"
    return json.loads(p.read_text()) if p.exists() else {}


def remaining(school: str) -> int:
    month = date.today().strftime("%Y-%m")
    return LIMIT - _usage().get(school.strip().lower(), {}).get(month, 0)


def register_use(school: str) -> None:
    DATA.mkdir(exist_ok=True)
    u = _usage()
    key, month = school.strip().lower(), date.today().strftime("%Y-%m")
    u.setdefault(key, {})[month] = u.get(key, {}).get(month, 0) + 1
    (DATA / "usage.json").write_text(json.dumps(u, indent=2))


def save_correction(record: dict) -> None:
    DATA.mkdir(exist_ok=True)
    with open(DATA / "corrections.jsonl", "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------- cache: never pay twice for the same audio or the same debate ----------
CACHE = DATA / "cache"


def cache_get(kind: str, key: str):
    p = CACHE / kind / f"{key}.json"
    return json.loads(p.read_text()) if p.exists() else None


def cache_put(kind: str, key: str, value) -> None:
    (CACHE / kind).mkdir(parents=True, exist_ok=True)
    (CACHE / kind / f"{key}.json").write_text(json.dumps(value, ensure_ascii=False))
