import json
import time
import random
from pathlib import Path

from tqdm import tqdm

from utils.vlr_client import VLRClient

# -----------------------------
# Configuration
# -----------------------------

MIN_DELAY = 3          # seconds
MAX_DELAY = 6          # seconds
MAX_RETRIES = 10

client = VLRClient()

# -----------------------------
# Load matches
# -----------------------------

with open("data/raw/matches.json", "r", encoding="utf-8") as f:
    matches = json.load(f)

output_dir = Path("data/raw/match_details")
output_dir.mkdir(parents=True, exist_ok=True)

remaining = [
    match for match in matches
    if not (output_dir / f"{match['match_id']}.json").exists()
]

print(f"Already downloaded: {len(matches) - len(remaining)}")
print(f"Remaining: {len(remaining)}")

failed = []

# -----------------------------
# Download loop
# -----------------------------

for match in tqdm(remaining, desc="Downloading match details"):

    match_id = match["match_id"]
    file_path = output_dir / f"{match_id}.json"

    success = False

    for attempt in range(MAX_RETRIES):

        try:

            detail = client.get_match_details(match_id)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(detail, f, indent=4)

            success = True

            # Random delay between successful requests
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

            break

        except Exception as e:

            error = str(e)

            # -----------------------------
            # Rate limit
            # -----------------------------
            if "429" in error:

                wait = min(30 * (attempt + 1), 300)

                print(f"\n⚠️ 429 Too Many Requests")
                print(f"Match: {match_id}")
                print(f"Retry {attempt + 1}/{MAX_RETRIES}")
                print(f"Waiting {wait} seconds...\n")

                time.sleep(wait)

                continue

            # -----------------------------
            # Other errors
            # -----------------------------
            else:

                print(f"\n❌ Failed {match_id}")
                print(error)

                break

    if not success:
        failed.append(match_id)

# -----------------------------
# Save failures
# -----------------------------

with open("data/raw/failed_matches.json", "w", encoding="utf-8") as f:
    json.dump(failed, f, indent=4)

print("\n=================================")
print("Download complete!")
print(f"Downloaded : {len(remaining) - len(failed)}")
print(f"Failed     : {len(failed)}")
print("=================================")