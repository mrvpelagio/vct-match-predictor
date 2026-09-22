import json
import sqlite3
from pathlib import Path

from tqdm import tqdm

DB_PATH = "database/vct.db"

# =====================================================
# Helper functions
# =====================================================

def safe_int(value):
    try:
        return int(str(value).replace("%", "").replace(",", ""))
    except:
        return None


def safe_float(value):
    try:
        return float(str(value).replace("%", "").replace(",", ""))
    except:
        return None


# =====================================================
# Database
# =====================================================

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# =====================================================
# Load match metadata
# =====================================================

with open("data/raw/matches.json", encoding="utf-8") as f:
    metadata = json.load(f)

match_lookup = {
    str(match["match_id"]): match
    for match in metadata
}

# =====================================================
# JSON files
# =====================================================

json_files = sorted(Path("data/raw/match_details").glob("*.json"))

print(f"Found {len(json_files)} downloaded matches.")

failed = []

# =====================================================
# Main loop
# =====================================================

for index, json_file in enumerate(tqdm(json_files), start=1):

    try:

        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        match = data["data"]["segments"][0]

        match_id = str(match["match_id"])

        if match_id not in match_lookup:
            continue

        meta = match_lookup[match_id]

        event_id = int(meta["event_id"])
        event_name = meta["event_name"]

        team1 = match["teams"][0]["name"]
        team2 = match["teams"][1]["name"]

        winner = (
            team1
            if match["teams"][0]["is_winner"]
            else team2
        )

        # =================================================
        # Event
        # =================================================

        cursor.execute("""
        INSERT OR IGNORE INTO events(
            event_id,
            event_name
        )
        VALUES (?, ?)
        """, (
            event_id,
            event_name
        ))

        # =================================================
        # Match
        # =================================================

        cursor.execute("""
        INSERT OR IGNORE INTO matches(
            match_id,
            event_id,
            date,
            team1,
            team2,
            winner
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            int(match_id),
            event_id,
            match["date"],
            team1,
            team2,
            winner
        ))

        # =================================================
        # Maps
        # =================================================

        for game_map in match["maps"]:

            map_name = game_map["map_name"].replace("PICK", "").strip()

            t1_score = safe_int(game_map["score"]["team1"])
            t2_score = safe_int(game_map["score"]["team2"])

            if t1_score is None or t2_score is None:
                continue

            map_winner = team1 if t1_score > t2_score else team2

            cursor.execute("""
            INSERT INTO maps(
                match_id,
                map_name,
                team1_score,
                team2_score,
                winner
            )
            VALUES (?, ?, ?, ?, ?)
            """, (
                int(match_id),
                map_name,
                t1_score,
                t2_score,
                map_winner
            ))

            # ---------------- Team 1 ----------------

            for player in game_map["players"]["team1"]:

                cursor.execute("""
                INSERT INTO players(
                    match_id,
                    map_name,
                    team,
                    player,
                    agent,
                    rating,
                    acs,
                    kills,
                    deaths,
                    assists,
                    adr,
                    kast,
                    hs_pct,
                    fk,
                    fd
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(match_id),
                    map_name,
                    team1,
                    player["name"],
                    player["agent"],
                    safe_float(player.get("rating")),
                    safe_int(player.get("acs")),
                    safe_int(player.get("kills")),
                    safe_int(player.get("deaths")),
                    safe_int(player.get("assists")),
                    safe_int(player.get("adr")),
                    safe_float(player.get("kast")),
                    safe_float(player.get("hs_pct")),
                    safe_int(player.get("fk")),
                    safe_int(player.get("fd"))
                ))

            # ---------------- Team 2 ----------------

            for player in game_map["players"]["team2"]:

                cursor.execute("""
                INSERT INTO players(
                    match_id,
                    map_name,
                    team,
                    player,
                    agent,
                    rating,
                    acs,
                    kills,
                    deaths,
                    assists,
                    adr,
                    kast,
                    hs_pct,
                    fk,
                    fd
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(match_id),
                    map_name,
                    team2,
                    player["name"],
                    player["agent"],
                    safe_float(player.get("rating")),
                    safe_int(player.get("acs")),
                    safe_int(player.get("kills")),
                    safe_int(player.get("deaths")),
                    safe_int(player.get("assists")),
                    safe_int(player.get("adr")),
                    safe_float(player.get("kast")),
                    safe_float(player.get("hs_pct")),
                    safe_int(player.get("fk")),
                    safe_int(player.get("fd"))
                ))

        # Commit every 100 matches
        if index % 100 == 0:
            conn.commit()

    except Exception as e:

        failed.append({
            "file": json_file.name,
            "error": str(e)
        })

# =====================================================
# Final commit
# =====================================================

conn.commit()
conn.close()

# =====================================================
# Save failed files
# =====================================================

with open("database/failed_ingest.json", "w", encoding="utf-8") as f:
    json.dump(failed, f, indent=4)

print("\n======================================")
print("Database ingestion complete!")
print(f"Processed : {len(json_files)}")
print(f"Failed    : {len(failed)}")
print("======================================")