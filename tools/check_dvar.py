"""Check the divrei Torah in data/weekly.json and data/bank.json: valid JSON and the exact tag layout of each style.

Usage: python3 tools/check_dvar.py   (exit code 1 on any problem)
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLES = {
    "pshat": ["פסוק", "קושיה", "מפרש", "חידוש", "מסר"],
    "chassidut": ["פסוק", "דיוק", "מפרש", "נקודה", "עבודה"],
    "mussar": ["פסוק", "התבוננות", "מפרש", "מידה", "קבלה"],
}


def check(text, style):
    errs, lines = [], text.split("\n")
    for p in ("כותרת:", "תקציר:", "מקורות:"):
        if sum(l.startswith(p) for l in lines) != 1:
            errs.append(f"'{p}' must appear exactly once")
    tags = [m.group(1) for l in lines if (m := re.match(r"^\[([^\]:]+)(?::\s*[^\]]+)?\]$", l))]
    if tags != STYLES[style]:
        errs.append(f"tags {tags} != {STYLES[style]}")
    if sum(l.count("[") + l.count("]") for l in lines) != 10:
        errs.append("square brackets used outside the five tag lines")
    if not lines[0].startswith("כותרת:") or not lines[-1].startswith("מקורות:"):
        errs.append("must start with 'כותרת:' and end with 'מקורות:'")
    if re.search(r"[֑-ׇ]", text):
        errs.append("contains niqqud or cantillation marks")
    return errs


def entries():
    weekly = json.loads((ROOT / "data/weekly.json").read_text(encoding="utf-8"))["entries"]
    bank = json.loads((ROOT / "data/bank.json").read_text(encoding="utf-8"))
    for date, e in weekly.items():
        styles = e.get("styles") or {"pshat": e.get("text", "")}
        for s, t in styles.items():
            yield f"weekly {date} {s}", s, t
    for k, v in bank.items():
        for s, t in ({"pshat": v} if isinstance(v, str) else v).items():
            yield f"bank {k} {s}", s, t


bad = 0
for name, style, text in entries():
    errs = [f"unknown style '{style}'"] if style not in STYLES else check(text, style)
    for e in errs:
        bad += 1
        print(f"{name}: {e}")
print("OK" if not bad else f"{bad} problem(s)")
sys.exit(1 if bad else 0)
