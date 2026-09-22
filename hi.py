import json

with open("data/processed/event_ids.json", encoding="utf-8") as f:
    events = json.load(f)

for event in events:
    print(event["id"], "-", event["name"])