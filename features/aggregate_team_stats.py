import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = "database/vct.db"

# ---------------------------------------------------
# Load player statistics
# ---------------------------------------------------

conn = sqlite3.connect(DB_PATH)

players = pd.read_sql("""
SELECT
    match_id,
    map_name,
    team,
    rating,
    acs,
    kast,
    adr,
    fk,
    fd
FROM players
""", conn)

conn.close()

print(f"Loaded {len(players):,} player rows.")

# ---------------------------------------------------
# Aggregate to TEAM level
# ---------------------------------------------------

team_stats = (
    players
    .groupby(
        [
            "match_id",
            "map_name",
            "team"
        ],
        as_index=False
    )
    .agg(
        avg_rating=("rating", "mean"),
        avg_acs=("acs", "mean"),
        avg_kast=("kast", "mean"),
        avg_adr=("adr", "mean"),
        avg_fk=("fk", "mean"),
        avg_fd=("fd", "mean")
    )
)

# ---------------------------------------------------
# Round values
# ---------------------------------------------------

numeric_cols = [
    "avg_rating",
    "avg_acs",
    "avg_kast",
    "avg_adr",
    "avg_fk",
    "avg_fd"
]

team_stats[numeric_cols] = (
    team_stats[numeric_cols]
    .round(2)
)

# ---------------------------------------------------
# Save
# ---------------------------------------------------

output_dir = Path("features")
output_dir.mkdir(exist_ok=True)

output_path = output_dir / "team_stats.csv"

team_stats.to_csv(
    output_path,
    index=False
)

print()

print("===================================")
print("Team statistics created!")
print("===================================")

print(f"Rows: {len(team_stats):,}")

print()

print(team_stats.head())

print()

print(f"Saved to {output_path}")