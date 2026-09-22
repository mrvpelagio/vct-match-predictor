import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline

# =====================================================
# Load dataset
# =====================================================

df = pd.read_csv("data/processed/dataset.csv")

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values("date").reset_index(drop=True)

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

    # NEW FEATURES
    "h2h_winrate",
    "h2h_matches",

    "avg_acs_diff",
    "avg_rating_diff",
    "avg_kast_diff",
    "avg_adr_diff",
    "avg_fk_diff",
    "avg_fd_diff"

]

TARGET = "winner"

split = int(len(df) * 0.8)

train = df.iloc[:split]
test = df.iloc[split:]

X_train = train[FEATURES]
X_test = test[FEATURES]

y_train = train[TARGET]
y_test = test[TARGET]

pipeline = Pipeline([

    (
        "imputer",
        SimpleImputer(strategy="mean")
    ),

    (
        "model",
        RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
    )

])

print("Training Random Forest...")

pipeline.fit(X_train, y_train)

predictions = pipeline.predict(X_test)

probabilities = pipeline.predict_proba(X_test)[:, 1]

print()

print("=" * 60)
print("Random Forest")
print("=" * 60)

print(f"Accuracy : {accuracy_score(y_test, predictions):.4f}")
print(f"Precision: {precision_score(y_test, predictions):.4f}")
print(f"Recall   : {recall_score(y_test, predictions):.4f}")
print(f"F1       : {f1_score(y_test, predictions):.4f}")
print(f"ROC AUC  : {roc_auc_score(y_test, probabilities):.4f}")

joblib.dump(
    pipeline,
    "models/random_forest.joblib"
)

print()
print("Saved model.")