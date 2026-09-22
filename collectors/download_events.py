import json
from pathlib import Path

from utils.vlr_client import VLRClient

client = VLRClient()

events = client.get_events()["data"]["segments"]

# Create data/raw if it doesn't exist
output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

# Save all events
with open(output_dir / "events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, indent=4)

print(f"✅ Saved {len(events)} events.")