import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

import pandas as pd
from tqdm import tqdm
from features.head_to_head import HeadToHead

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

print(f"Loaded {len(matches)} matches.")

# =====================================================
# Load event years
# =====================================================

with open("data/processed/event_ids.json", encoding="utf-8") as f:
    events = json.load(f)

event_year = {}

for event in events:

    m = re.search(r"(20\d{2})", event["name"])

    if m:
        event_year[int(event["id"])] = m.group(1)

# =====================================================
# Parse dates
# =====================================================

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
    lambda row: parse_date(
        row["date"],
        row["event_id"]
    ),
    axis=1
)

# =====================================================
# Remove future matches
# =====================================================

matches = matches[
    (matches["winner"].notna()) &
    (matches["team1"] != "TBD") &
    (matches["team2"] != "TBD")
].copy()

# =====================================================
# Sort chronologically
# =====================================================

matches = (
    matches
    .sort_values("date")
    .reset_index(drop=True)
)

print(f"Completed matches: {len(matches)}")

# =====================================================
# Load aggregated match statistics
# =====================================================

match_stats = pd.read_csv("features/match_stats.csv")

print(f"Loaded {len(match_stats)} team statistics.")

# =====================================================
# Team histories
# =====================================================

histories = defaultdict(TeamHistory)

head_to_head = HeadToHead()

# =====================================================
# Dataset
# =====================================================

dataset = []

import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

import pandas as pd
from tqdm import tqdm

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

print(f"Loaded {len(matches)} matches.")

# =====================================================
# Load event years
# =====================================================

with open("data/processed/event_ids.json", encoding="utf-8") as f:
    events = json.load(f)

event_year = {}

for event in events:

    m = re.search(r"(20\d{2})", event["name"])

    if m:
        event_year[int(event["id"])] = m.group(1)

# =====================================================
# Parse dates
# =====================================================

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
    lambda row: parse_date(
        row["date"],
        row["event_id"]
    ),
    axis=1
)

# =====================================================
# Remove future matches
# =====================================================

matches = matches[
    (matches["winner"].notna()) &
    (matches["team1"] != "TBD") &
    (matches["team2"] != "TBD")
].copy()

# =====================================================
# Sort chronologically
# =====================================================

matches = (
    matches
    .sort_values("date")
    .reset_index(drop=True)
)

print(f"Completed matches: {len(matches)}")

# =====================================================
# Load aggregated match statistics
# =====================================================

match_stats = pd.read_csv("features/match_stats.csv")

print(f"Loaded {len(match_stats)} team statistics.")

# =====================================================
# Team histories
# =====================================================

histories = defaultdict(TeamHistory)

# =====================================================
# Dataset
# =====================================================

dataset = []

# =====================================================
# Feature extraction
# =====================================================

def extract_features(history, prefix):
    """
    Extract all historical features from a TeamHistory object.
    """

    return {

        f"{prefix}_elo": history.elo,

        f"{prefix}_last5_wr": history.last5_winrate(),

        f"{prefix}_avg_acs": history.avg_acs(),

        f"{prefix}_avg_rating": history.avg_rating(),

        f"{prefix}_avg_kast": history.avg_kast(),

        f"{prefix}_avg_adr": history.avg_adr(),

        f"{prefix}_avg_fk": history.avg_fk(),

        f"{prefix}_avg_fd": history.avg_fd(),

    }


# =====================================================
# Elo
# =====================================================

K = 32


def expected_score(rating_a, rating_b):

    return 1 / (
        1 + 10 ** ((rating_b - rating_a) / 400)
    )


def update_elo(history1, history2, result1, result2):

    expected1 = expected_score(
        history1.elo,
        history2.elo
    )

    expected2 = expected_score(
        history2.elo,
        history1.elo
    )

    history1.elo += K * (result1 - expected1)

    history2.elo += K * (result2 - expected2)

# =====================================================
# Build dataset
# =====================================================

for _, match in tqdm(
    matches.iterrows(),
    total=len(matches),
    desc="Generating features"
):

    match_id = match["match_id"]

    team1 = match["team1"]
    team2 = match["team2"]

    winner = match["winner"]

    # ------------------------------------------

    history1 = histories[team1]

    history2 = histories[team2]

    # ------------------------------------------
    # Current match statistics
    # ------------------------------------------

    team1_stats = match_stats[
        (match_stats.match_id == match_id) &
        (match_stats.team == team1)
    ]

    team2_stats = match_stats[
        (match_stats.match_id == match_id) &
        (match_stats.team == team2)
    ]

    if len(team1_stats) == 0 or len(team2_stats) == 0:
        continue

    team1_stats = team1_stats.iloc[0]
    team2_stats = team2_stats.iloc[0]

    # ------------------------------------------
    # Match result
    # ------------------------------------------

    if winner == team1:

        result1 = 1
        result2 = 0

        target = 1

    else:

        result1 = 0
        result2 = 1

        target = 0

    h2h_winrate, h2h_matches = head_to_head.get_stats(
        team1,
        team2
    )

    # ------------------------------------------
    # Feature row
    # ------------------------------------------

    row = {

        "match_id": match_id,

        "date": match["date"],

        "team1": team1,

        "team2": team2,

        "winner": target,

        "h2h_winrate": h2h_winrate,

        "h2h_matches": h2h_matches

    }

    row.update(
        extract_features(history1, "team1")
    )

    row.update(
        extract_features(history2, "team2")
    )

    # ------------------------------------------
    # Difference features
    # ------------------------------------------

    numeric_pairs = [

        ("elo", "elo"),

        ("last5_wr", "last5_wr"),

        ("avg_acs", "avg_acs"),

        ("avg_rating", "avg_rating"),

        ("avg_kast", "avg_kast"),

        ("avg_adr", "avg_adr"),

        ("avg_fk", "avg_fk"),

        ("avg_fd", "avg_fd")

    ]

    for left, right in numeric_pairs:

        a = row[f"team1_{left}"]

        b = row[f"team2_{right}"]

        if a is None or b is None:

            row[f"{left}_diff"] = None

        else:

            row[f"{left}_diff"] = a - b

    dataset.append(row)

    # ------------------------------------------
    # Update Elo
    # ------------------------------------------

    update_elo(
        history1,
        history2,
        result1,
        result2
    )

    # ------------------------------------------
    # Update histories
    # ------------------------------------------

    history1.update(
        win=result1,
        acs=team1_stats.avg_acs,
        rating=team1_stats.avg_rating,
        kast=team1_stats.avg_kast,
        adr=team1_stats.avg_adr,
        fk=team1_stats.avg_fk,
        fd=team1_stats.avg_fd
    )

    history2.update(
        win=result2,
        acs=team2_stats.avg_acs,
        rating=team2_stats.avg_rating,
        kast=team2_stats.avg_kast,
        adr=team2_stats.avg_adr,
        fk=team2_stats.avg_fk,
        fd=team2_stats.avg_fd
    )

    head_to_head.update(
        team1,
        team2,
        winner
    )

# =====================================================
# Save dataset
# =====================================================

dataset = pd.DataFrame(dataset)

output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "dataset.csv"

dataset.to_csv(
    output_path,
    index=False
)

print()

print("=" * 60)

print("Feature engineering complete!")

print("=" * 60)

print()

print(f"Rows: {len(dataset):,}")

print(f"Columns: {len(dataset.columns)}")

print()

print(dataset.head())

print()

print(f"Saved to {output_path}")