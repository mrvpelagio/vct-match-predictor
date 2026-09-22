import joblib
import pandas as pd
import matplotlib.pyplot as plt

# Load model
pipeline = joblib.load("models/random_forest.joblib")

model = pipeline.named_steps["model"]

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

    "avg_acs_diff",
    "avg_rating_diff",
    "avg_kast_diff",
    "avg_adr_diff",
    "avg_fk_diff",
    "avg_fd_diff"

]

importance = pd.DataFrame({
    "Feature": FEATURES,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    "Importance",
    ascending=False
)

print(importance)

plt.figure(figsize=(10,8))

plt.barh(
    importance["Feature"],
    importance["Importance"]
)

plt.gca().invert_yaxis()

plt.tight_layout()

plt.show()