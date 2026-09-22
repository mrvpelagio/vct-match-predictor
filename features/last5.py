import sqlite3
from collections import defaultdict, deque

import pandas as pd

DB_PATH = "database/vct.db"

WINDOW = 5

# ----------------------------------------
# Load matches
# ----------------------------------------

conn = sqlite3.connect(DB_PATH)

matches = pd.read_sql("""
SELECT
    match_id,
    date,
    team1,
    team2,
    winner
FROM matches
""", conn)

conn.close()

matches = matches.sort_values("date").reset_index(drop=True)

# ----------------------------------------
# Team history
# ----------------------------------------

history = defaultdict(lambda: deque(maxlen=WINDOW))

rows = []

# ----------------------------------------
# Build feature
# ----------------------------------------

for _, match in matches.iterrows():

    team1 = match["team1"]
    team2 = match["team2"]

    # -------- team1 win rate --------

    if len(history[team1]) == 0:
        team1_wr = 0.5
    else:
        team1_wr = sum(history[team1]) / len(history[team1])

    # -------- team2 win rate --------

    if len(history[team2]) == 0:
        team2_wr = 0.5
    else:
        team2_wr = sum(history[team2]) / len(history[team2])

    rows.append({

        "match_id": match["match_id"],

        "team1_last5_wr": team1_wr,

        "team2_last5_wr": team2_wr

    })

    # ----------------------------------------
    # Update histories AFTER saving features
    # ----------------------------------------

    if match["winner"] == team1:

        history[team1].append(1)
        history[team2].append(0)

    else:

        history[team1].append(0)
        history[team2].append(1)

# ----------------------------------------
# Save
# ----------------------------------------

df = pd.DataFrame(rows)

df.to_csv(
    "features/last5_dataset.csv",
    index=False
)

print(df.head())

print()

print(f"Matches: {len(df)}")

print("Saved features/last5_dataset.csv")