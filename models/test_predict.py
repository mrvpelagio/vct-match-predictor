import joblib
import pandas as pd

#load model 

pipeline = joblib.load("models/random_forest.joblib")


#read data set 

df = pd.read_csv("data/processed/dataset.csv")

#features 


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

    # NEW FEATURES 8/3
    "h2h_winrate",
    "h2h_matches",

    "avg_acs_diff",
    "avg_rating_diff",
    "avg_kast_diff",
    "avg_adr_diff",
    "avg_fk_diff",
    "avg_fd_diff"

]

#prediction pipeline 

row = df.iloc[24] 

prediction = pipeline.predict(pd.DataFrame([row[FEATURES]]))[0]

print(f"Match {row['team1']} vs {row['team2']}")
print(f"Actual winner: {'team 1' if row['winner'] == 1 else 'team 2'}")
print(f"Predicted winner: {'team 1' if prediction == 1 else 'team 2'}")
