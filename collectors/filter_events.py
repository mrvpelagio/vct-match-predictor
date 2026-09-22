import json
from pathlib import Path

EVENT_KEYWORDS = [
    "VCT",
    "Masters",
    "Champions",
    "Kickoff",
]

with open("data/raw/events.json", encoding="utf-8") as f:
    events = json.load(f)

vct_events = [
    event
    for event in events
    if any(keyword in event["title"] for keyword in EVENT_KEYWORDS)
]

print(f"Found {len(vct_events)} VCT events.")

Path("data/processed").mkdir(parents=True, exist_ok=True)

with open("data/processed/vct_events.json", "w", encoding="utf-8") as f:
    json.dump(vct_events, f, indent=4)

print("✅ Saved filtered VCT events.")