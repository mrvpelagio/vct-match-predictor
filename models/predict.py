import sqlite3
import json
import re
from collections import defaultdict

import joblib
import pandas as pd

from features.team_history import TeamHistory
from features.head_to_head import HeadToHead


# =====================================================
# Configuration
# =====================================================

DB_PATH = "database/vct.db"
MODEL_PATH = "models/random_forest.joblib"
EVENTS_PATH = "data/processed/event_ids.json"
MATCH_STATS_PATH = "features/match_stats.csv"


FEATURES = [
    "team1_elo",
    "team2_elo",

    "team1_last5_wr",
    "team2_last5_wr",

    "team1_avg_acs",
    "team2_avg_acs",

    "team1_avg_rating",
    "team2_avg_rating",

    "team1_avg_kast",
    "team2_avg_kast",

    "team1_avg_adr",
    "team2_avg_adr",

    "team1_avg_fk",
    "team2_avg_fk",

    "team1_avg_fd",
    "team2_avg_fd",

    "elo_diff",
    "last5_wr_diff",

    "h2h_winrate",
    "h2h_matches",

    "avg_acs_diff",
    "avg_rating_diff",
    "avg_kast_diff",
    "avg_adr_diff",
    "avg_fk_diff",
    "avg_fd_diff",
]


# =====================================================
# Date parsing
# =====================================================

def load_event_years():

    with open(EVENTS_PATH, encoding="utf-8") as f:
        events = json.load(f)

    event_year = {}

    for event in events:

        match = re.search(r"(20\d{2})", event["name"])

        if match:
            event_year[int(event["id"])] = match.group(1)

    return event_year


def parse_date(date_string, event_id, event_year):

    date_string = re.sub(
        r"\s+PST.*$",
        "",
        date_string
    )

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
# Rebuild historical team states
# =====================================================

def rebuild_histories():

    print("Loading historical matches...")

    conn = sqlite3.connect(DB_PATH)

    matches = pd.read_sql(
        """
        SELECT
            match_id,
            event_id,
            date,
            team1,
            team2,
            winner
        FROM matches
        """,
        conn
    )

    conn.close()

    event_year = load_event_years()

    matches["date"] = matches.apply(
        lambda row: parse_date(
            row["date"],
            row["event_id"],
            event_year
        ),
        axis=1
    )

    matches = matches[
        (matches["winner"].notna()) &
        (matches["team1"] != "TBD") &
        (matches["team2"] != "TBD")
    ].copy()

    matches = (
        matches
        .sort_values("date")
        .reset_index(drop=True)
    )

    print(f"Completed matches: {len(matches)}")

    match_stats = pd.read_csv(
        MATCH_STATS_PATH
    )

    histories = defaultdict(TeamHistory)

    head_to_head = HeadToHead()

    for _, match in matches.iterrows():

        match_id = match["match_id"]

        team1 = match["team1"]
        team2 = match["team2"]

        winner = match["winner"]

        history1 = histories[team1]
        history2 = histories[team2]

        # ---------------------------------------------
        # Get match statistics
        # ---------------------------------------------

        team1_stats = match_stats[
            (match_stats.match_id == match_id) &
            (match_stats.team == team1)
        ]

        team2_stats = match_stats[
            (match_stats.match_id == match_id) &
            (match_stats.team == team2)
        ]

        # Same behavior as feature engineering:
        # skip matches without statistics.

        if len(team1_stats) == 0 or len(team2_stats) == 0:
            continue

        team1_stats = team1_stats.iloc[0]
        team2_stats = team2_stats.iloc[0]

        # ---------------------------------------------
        # Result
        # ---------------------------------------------

        if winner == team1:

            result1 = 1
            result2 = 0

        else:

            result1 = 0
            result2 = 1

        # ---------------------------------------------
        # Update Elo
        # ---------------------------------------------

        update_elo(
            history1,
            history2,
            result1,
            result2
        )

        # ---------------------------------------------
        # Update team histories
        # ---------------------------------------------

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

        # ---------------------------------------------
        # Update H2H
        # ---------------------------------------------

        head_to_head.update(
            team1,
            team2,
            winner
        )

    return histories, head_to_head


# =====================================================
# Build prediction features
# =====================================================

def build_features(
    team1,
    team2,
    histories,
    head_to_head
):

    history1 = histories[team1]
    history2 = histories[team2]

    # ---------------------------------------------
    # H2H
    # ---------------------------------------------

    h2h_winrate, h2h_matches = (
        head_to_head.get_stats(
            team1,
            team2
        )
    )

    # ---------------------------------------------
    # Team features
    # ---------------------------------------------

    team1_elo = history1.elo
    team2_elo = history2.elo

    team1_last5_wr = history1.last5_winrate()
    team2_last5_wr = history2.last5_winrate()

    team1_avg_acs = history1.avg_acs()
    team2_avg_acs = history2.avg_acs()

    team1_avg_rating = history1.avg_rating()
    team2_avg_rating = history2.avg_rating()

    team1_avg_kast = history1.avg_kast()
    team2_avg_kast = history2.avg_kast()

    team1_avg_adr = history1.avg_adr()
    team2_avg_adr = history2.avg_adr()

    team1_avg_fk = history1.avg_fk()
    team2_avg_fk = history2.avg_fk()

    team1_avg_fd = history1.avg_fd()
    team2_avg_fd = history2.avg_fd()

    # ---------------------------------------------
    # Difference features
    # ---------------------------------------------

    def difference(a, b):

        if a is None or b is None:
            return None

        return a - b

    row = {

        "team1_elo": team1_elo,
        "team2_elo": team2_elo,

        "team1_last5_wr": team1_last5_wr,
        "team2_last5_wr": team2_last5_wr,

        "team1_avg_acs": team1_avg_acs,
        "team2_avg_acs": team2_avg_acs,

        "team1_avg_rating": team1_avg_rating,
        "team2_avg_rating": team2_avg_rating,

        "team1_avg_kast": team1_avg_kast,
        "team2_avg_kast": team2_avg_kast,

        "team1_avg_adr": team1_avg_adr,
        "team2_avg_adr": team2_avg_adr,

        "team1_avg_fk": team1_avg_fk,
        "team2_avg_fk": team2_avg_fk,

        "team1_avg_fd": team1_avg_fd,
        "team2_avg_fd": team2_avg_fd,

        "elo_diff": team1_elo - team2_elo,

        "last5_wr_diff": (
            team1_last5_wr -
            team2_last5_wr
        ),

        "h2h_winrate": h2h_winrate,

        "h2h_matches": h2h_matches,

        "avg_acs_diff": difference(
            team1_avg_acs,
            team2_avg_acs
        ),

        "avg_rating_diff": difference(
            team1_avg_rating,
            team2_avg_rating
        ),

        "avg_kast_diff": difference(
            team1_avg_kast,
            team2_avg_kast
        ),

        "avg_adr_diff": difference(
            team1_avg_adr,
            team2_avg_adr
        ),

        "avg_fk_diff": difference(
            team1_avg_fk,
            team2_avg_fk
        ),

        "avg_fd_diff": difference(
            team1_avg_fd,
            team2_avg_fd
        ),
    }

    return pd.DataFrame(
        [row],
        columns=FEATURES
    )


# =====================================================
# Main predictor
# =====================================================

def main():

    print("=" * 60)
    print("VCT MATCH PREDICTOR")
    print("=" * 60)

    print()
    print("Rebuilding team histories...")
    print()

    histories, head_to_head = rebuild_histories()

    print()
    print("Loading Random Forest model...")

    model = joblib.load(MODEL_PATH)

    print("Model loaded.")

    print()

    # ---------------------------------------------
    # Get user input
    # ---------------------------------------------

    team1 = input("Team 1: ").strip()
    team2 = input("Team 2: ").strip()

    if team1 not in histories:

        print()
        print(f"Team not found: {team1}")
        return

    if team2 not in histories:

        print()
        print(f"Team not found: {team2}")
        return

    if team1 == team2:

        print()
        print("Please choose two different teams.")
        return

    # ---------------------------------------------
    # Build features
    # ---------------------------------------------

    X = build_features(
        team1,
        team2,
        histories,
        head_to_head
    )

    # ---------------------------------------------
    # Predict
    # ---------------------------------------------

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    team2_probability = probabilities[0]
    team1_probability = probabilities[1]

    predicted_winner = (
        team1
        if prediction == 1
        else team2
    )

    # ---------------------------------------------
    # Results
    # ---------------------------------------------

    print()
    print("=" * 60)
    print("PREDICTION")
    print("=" * 60)

    print()

    print(
        f"{team1}: "
        f"{team1_probability * 100:.1f}%"
    )

    print(
        f"{team2}: "
        f"{team2_probability * 100:.1f}%"
    )

    print()

    print(
        f"Predicted Winner: {predicted_winner}"
    )

    print()

    # ---------------------------------------------
    # Show useful model features
    # ---------------------------------------------

    print("=" * 60)
    print("MATCH FEATURES")
    print("=" * 60)

    print()

    print(
        f"{team1} Elo: "
        f"{team1_elo if False else X.iloc[0]['team1_elo']:.1f}"
    )

    print(
        f"{team2} Elo: "
        f"{X.iloc[0]['team2_elo']:.1f}"
    )

    print(
        f"H2H Matches: "
        f"{int(X.iloc[0]['h2h_matches'])}"
    )

    print(
        f"H2H Win Rate ({team1}): "
        f"{X.iloc[0]['h2h_winrate'] * 100:.1f}%"
    )


if __name__ == "__main__":
    main()