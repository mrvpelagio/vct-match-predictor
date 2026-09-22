import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Load map-level team statistics
# --------------------------------------------------

team_stats = pd.read_csv("features/team_stats.csv")

print(f"Loaded {len(team_stats):,} team-map rows.")

# --------------------------------------------------
# Aggregate to one row per team per match
# --------------------------------------------------

match_stats = (
    team_stats
    .groupby(
        ["match_id", "team"],
        as_index=False
    )
    .agg(
        avg_rating=("avg_rating", "mean"),
        avg_acs=("avg_acs", "mean"),
        avg_kast=("avg_kast", "mean"),
        avg_adr=("avg_adr", "mean"),
        avg_fk=("avg_fk", "mean"),
        avg_fd=("avg_fd", "mean")
    )
)

numeric_cols = [
    "avg_rating",
    "avg_acs",
    "avg_kast",
    "avg_adr",
    "avg_fk",
    "avg_fd"
]

match_stats[numeric_cols] = (
    match_stats[numeric_cols]
    .round(2)
)

output = Path("features/match_stats.csv")

match_stats.to_csv(
    output,
    index=False
)

print()
print("===================================")
print("Match statistics created!")
print("===================================")
print(f"Rows: {len(match_stats):,}")
print()
print(match_stats.head())
print()
print(f"Saved to {output}")