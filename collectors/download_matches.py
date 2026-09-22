import json
from pathlib import Path

from tqdm import tqdm

from config import VALID_EVENT_IDS
from utils.vlr_client import VLRClient

client = VLRClient()

# -----------------------------
# Load ALL historical events
# -----------------------------

with open("data/processed/event_ids.json", "r", encoding="utf-8") as f:
    events = json.load(f)

# Keep only Tier 1 VCT events
events = [
    event
    for event in events
    if int(event["id"]) in VALID_EVENT_IDS
]

print(f"Using {len(events)} Tier 1 VCT events.")

# -----------------------------
# Download matches
# -----------------------------

all_matches = []

for event in tqdm(events, desc="Downloading matches"):

    event_id = event["id"]

    try:

        response = client.get_event_matches(event_id)

        matches = response["data"]["segments"]

        for match in matches:
            match["event_id"] = event_id
            match["event_name"] = event["name"]

        all_matches.extend(matches)

    except Exception as e:
        print(f"Failed event {event_id}: {e}")

# -----------------------------
# Remove duplicate matches
# -----------------------------

unique_matches = {}

for match in all_matches:
    unique_matches[match["match_id"]] = match

all_matches = list(unique_matches.values())

print(f"Downloaded {len(all_matches)} unique matches.")

# -----------------------------
# Save
# -----------------------------

output = Path("data/raw")
output.mkdir(parents=True, exist_ok=True)

with open(output / "matches.json", "w", encoding="utf-8") as f:
    json.dump(all_matches, f, indent=4)

print("✅ Saved matches.json")