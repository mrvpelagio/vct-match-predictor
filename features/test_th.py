import json
import sqlite3
from collections import defaultdict

import pandas as pd

from features.team_history import TeamHistory

DB_PATH = "database/vct.db"

# =====================================================
# Load matches
# =====================================================

conn = sqlite3.connect(DB_PATH)

matches = pd.read_sql("""
SELECT
    match_id,
    event_id,
    date,
    team1,
    team2,
    winner
FROM matches
""", conn)

conn.close()

# =====================================================
# Parse dates
# =====================================================

import re

with open("data/processed/event_ids.json", encoding="utf-8") as f:
    events = json.load(f)

event_year = {}

for event in events:
    m = re.search(r"(20\d{2})", event["name"])
    if m:
        event_year[int(event["id"])] = m.group(1)


def parse_date(date_string, event_id):

    date_string = re.sub(r"\s+PST.*$", "", date_string)

    if re.search(r"20\d{2}", date_string):

        return pd.to_datetime(
            date_string,
            format="%B %d, %Y %I:%M %p"
        )

    year = event_year[int(event_id)]

    date_string = re.sub(
        r"^[A-Za-z]+,\s*",
        "",
        date_string
    )

    date_string = f"{date_string}, {year}"

    return pd.to_datetime(
        date_string,
        format="%B %d %I:%M %p, %Y"
    )


matches["date"] = matches.apply(
    lambda row: parse_date(row["date"], row["event_id"]),
    axis=1
)

matches = (
    matches
    .sort_values("date")
    .reset_index(drop=True)
)

matches = matches[
    (matches["team1"] != "TBD") &
    (matches["team2"] != "TBD") &
    (matches["winner"].notna())
]

# =====================================================
# Load match stats
# =====================================================

stats = pd.read_csv("features/match_stats.csv")

# =====================================================
# Team histories
# =====================================================

histories = defaultdict(TeamHistory)

# =====================================================
# Test first 10 matches
# =====================================================

for _, match in matches.head(10).iterrows():

    match_id = match["match_id"]

    team1 = match["team1"]
    team2 = match["team2"]

    h1 = histories[team1]
    h2 = histories[team2]

    print("=" * 70)
    print(f"{team1} vs {team2}")
    print()

    print("BEFORE")

    print(f"{team1}")
    print(f"  Elo: {h1.elo}")
    print(f"  Last5 WR: {h1.last5_winrate():.2f}")

    print()

    print(f"{team2}")
    print(f"  Elo: {h2.elo}")
    print(f"  Last5 WR: {h2.last5_winrate():.2f}")

    # -------------------------------------------------

    team1_stats = stats[
        (stats.match_id == match_id) &
        (stats.team == team1)
    ]

    team2_stats = stats[
        (stats.match_id == match_id) &
        (stats.team == team2)
    ]

    if len(team1_stats) == 0 or len(team2_stats) == 0:
        print("Missing stats.")
        continue

    s1 = team1_stats.iloc[0]
    s2 = team2_stats.iloc[0]

    winner = match["winner"]

    if winner == team1:

        result1 = 1
        result2 = 0

    else:

        result1 = 0
        result2 = 1

    # -------------------------------------------------
    # Simple Elo update
    # -------------------------------------------------

    K = 32

    expected1 = 1 / (1 + 10 ** ((h2.elo - h1.elo) / 400))
    expected2 = 1 / (1 + 10 ** ((h1.elo - h2.elo) / 400))

    h1.elo += K * (result1 - expected1)
    h2.elo += K * (result2 - expected2)

    # -------------------------------------------------
    # Update histories
    # -------------------------------------------------

    h1.update(
        win=result1,
        acs=s1.avg_acs,
        rating=s1.avg_rating,
        kast=s1.avg_kast,
        adr=s1.avg_adr,
        fk=s1.avg_fk,
        fd=s1.avg_fd
    )

    h2.update(
        win=result2,
        acs=s2.avg_acs,
        rating=s2.avg_rating,
        kast=s2.avg_kast,
        adr=s2.avg_adr,
        fk=s2.avg_fk,
        fd=s2.avg_fd
    )

    print()
    print("AFTER")

    print(f"{team1}")
    print(f"  Elo: {h1.elo:.1f}")
    print(f"  Last5 WR: {h1.last5_winrate():.2f}")
    print(f"  Avg ACS: {h1.avg_acs():.1f}")

    print()

    print(f"{team2}")
    print(f"  Elo: {h2.elo:.1f}")
    print(f"  Last5 WR: {h2.last5_winrate():.2f}")
    print(f"  Avg ACS: {h2.avg_acs():.1f}")

    print()