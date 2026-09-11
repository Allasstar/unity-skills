import glob
import json
import os
import re
import sys
from datetime import datetime, timedelta

IDLE_CAP = 900
WINDOW = timedelta(hours=5)


def transcripts_dir(project_dir):
    mangled = re.sub(r"[:\\/ ]", "-", os.path.abspath(project_dir).rstrip("\\/"))
    return os.path.join(os.path.expanduser("~/.claude/projects"), mangled)


def load_events(root):
    events = []
    for path in glob.glob(root + "/*.jsonl") + glob.glob(root + "/*/subagents/*.jsonl"):
        with open(path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                t = e.get("timestamp")
                if not t:
                    continue
                m = e.get("message")
                out = 0
                if isinstance(m, dict) and e.get("type") == "assistant" and m.get("usage"):
                    out = m["usage"].get("output_tokens") or 0
                events.append((datetime.fromisoformat(t.replace("Z", "+00:00")), out))
    return sorted(events)


def pct(values, p):
    return values[min(len(values) - 1, int(len(values) * p))]


def main(project_dir):
    root = transcripts_dir(project_dir)
    events = load_events(root)
    if not events:
        sys.exit(f"no transcripts in {root}")

    blocks = []
    for dt, out in events:
        if not blocks or dt >= blocks[-1]["start"] + WINDOW:
            blocks.append({"start": dt, "last": dt, "active": 0.0, "out": 0})
        b = blocks[-1]
        b["active"] += min((dt - b["last"]).total_seconds(), IDLE_CAP) / 3600
        b["last"] = dt
        b["out"] += out
    blocks = [b for b in blocks if b["active"] > 0.05]

    active = sorted(b["active"] for b in blocks)
    total_active = sum(active)
    total_out = sum(b["out"] for b in blocks)
    first, last = events[0][0].date(), events[-1][0].date()
    weekdays = sum(1 for i in range((last - first).days + 1) if (first + timedelta(days=i)).weekday() < 5)

    print(f"transcripts   {root}")
    print(f"span          {first} -> {last}, {weekdays} weekdays")
    print(f"active AI h   {total_active:.1f} total, {total_active / weekdays:.2f} per weekday")
    print(f"5h windows    {len(blocks)}; active h median {pct(active, .5):.2f}, p75 {pct(active, .75):.2f}, "
          f"p90 {pct(active, .9):.2f}, max {active[-1]:.2f}")
    print(f"output tokens {total_out / total_active / 1000:.0f}k per active h")
    print("pro_window_ai_hours ~ median active h per window if most windows hit the limit, else p75-p90")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
