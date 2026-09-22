import sqlite3
import pandas as pd

DB_PATH = "database/vct.db"

INITIAL_ELO = 1500
K = 32

# --------------------------------------
# Connect
# --------------------------------------

conn = sqlite3.connect(DB_PATH)

matches = pd.read_sql_query("""
SELECT
    match_id,
    date,
    team1,
    team2,
    winner
FROM matches
""", conn)

conn.close()

# --------------------------------------
# Sort chronologically
# --------------------------------------

matches = matches.sort_values("date").reset_index(drop=True)

# --------------------------------------
# Elo dictionary
# --------------------------------------

elo = {}

rows = []

# --------------------------------------
# Expected score
# --------------------------------------

def expected(a, b):
    return 1 / (1 + 10 ** ((b - a) / 400))

# --------------------------------------
# Process every match
# --------------------------------------

for _, match in matches.iterrows():

    team1 = match["team1"]
    team2 = match["team2"]

    elo.setdefault(team1, INITIAL_ELO)
    elo.setdefault(team2, INITIAL_ELO)

    r1 = elo[team1]
    r2 = elo[team2]

    e1 = expected(r1, r2)
    e2 = expected(r2, r1)

    if match["winner"] == team1:
        s1 = 1
        s2 = 0
    else:
        s1 = 0
        s2 = 1

    new_r1 = r1 + K * (s1 - e1)
    new_r2 = r2 + K * (s2 - e2)

    rows.append({
        "match_id": match["match_id"],
        "team1": team1,
        "team2": team2,
        "team1_elo_before": r1,
        "team2_elo_before": r2,
        "team1_elo_after": new_r1,
        "team2_elo_after": new_r2,
        "winner": match["winner"]
    })

    elo[team1] = new_r1
    elo[team2] = new_r2

# --------------------------------------
# Save
# --------------------------------------

elo_df = pd.DataFrame(rows)

elo_df.to_csv(
    "features/elo_dataset.csv",
    index=False
)

print(elo_df.head())

print()

print(f"Teams: {len(elo)}")

print(f"Matches: {len(elo_df)}")

print()

print("Saved features/elo_dataset.csv")