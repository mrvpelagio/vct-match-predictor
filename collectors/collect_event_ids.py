import json
from pathlib import Path

from utils.vlr_client import VLRClient

client = VLRClient()

# -----------------------------
# Search queries
# -----------------------------

YEARS = [2023, 2024, 2025, 2026]

REGIONS = [
    "Pacific",
    "Americas",
    "EMEA",
    "China",
    "Masters",
    "Champions",
]

queries = [
    f"{region} {year}"
    for year in YEARS
    for region in REGIONS
]

# -----------------------------
# Keywords
# -----------------------------

INCLUDE = [
    "VCT",
    "Champions Tour",
    "Masters",
    "Champions",
]

EXCLUDE = [
    "Game Changers",
    "Ascension",
    "College",
    "Saudi",
    "Predator",
    "Spotlight",
    "OFF//SEASON",
]

# -----------------------------
# Collect events
# -----------------------------

events = {}

for query in queries:

    print(f"Searching: {query}")

    try:
        response = client.search(query)

        results = response["data"]["segments"]["results"]["events"]

        for event in results:

            name = event["name"]

            # Skip unwanted tournaments
            if not any(x in name for x in INCLUDE):
                continue

            if any(x in name for x in EXCLUDE):
                continue

            events[event["id"]] = event

    except Exception as e:
        print(f"Failed on {query}: {e}")

# -----------------------------
# Sort events
# -----------------------------

events = sorted(
    events.values(),
    key=lambda x: int(x["id"])
)

print(f"\nCollected {len(events)} unique events.")

# -----------------------------
# Save
# -----------------------------

output = Path("data/processed")
output.mkdir(parents=True, exist_ok=True)

with open(output / "event_ids.json", "w", encoding="utf-8") as f:
    json.dump(events, f, indent=4)

print("Saved data/processed/event_ids.json")