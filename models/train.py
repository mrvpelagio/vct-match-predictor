import joblib
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# =====================================================
# Load dataset
# =====================================================

df = pd.read_csv("data/processed/dataset.csv")

print(f"Loaded {len(df)} matches.")

# =====================================================
# Dates
# =====================================================

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values("date").reset_index(drop=True)

# =====================================================
# Feature columns
# =====================================================
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

# =====================================================
# Chronological split
# =====================================================

split = int(len(df) * 0.8)

train = df.iloc[:split]

test = df.iloc[split:]

X_train = train[FEATURES]
X_test = test[FEATURES]

y_train = train[TARGET]
y_test = test[TARGET]

print()

print("Training:", len(train))
print("Testing :", len(test))

# =====================================================
# Pipeline
# =====================================================

pipeline = Pipeline([

    (
        "imputer",
        SimpleImputer(strategy="mean")
    ),

    (
        "scaler",
        StandardScaler()
    ),

    (
        "model",
        LogisticRegression(
            random_state=42,
            max_iter=2000
        )
    )

])

print()
print("Training Logistic Regression...")

pipeline.fit(
    X_train,
    y_train
)

print("Done!")

# =====================================================
# Predict
# =====================================================

predictions = pipeline.predict(X_test)

probabilities = pipeline.predict_proba(X_test)[:, 1]

# =====================================================
# Metrics
# =====================================================

print()
print("=" * 60)
print("Evaluation")
print("=" * 60)

print(f"Accuracy : {accuracy_score(y_test, predictions):.4f}")

print(f"Precision: {precision_score(y_test, predictions):.4f}")

print(f"Recall   : {recall_score(y_test, predictions):.4f}")

print(f"F1       : {f1_score(y_test, predictions):.4f}")

print(f"ROC AUC  : {roc_auc_score(y_test, probabilities):.4f}")

# =====================================================
# Save model
# =====================================================

joblib.dump(
    pipeline,
    "models/logistic_regression.joblib"
)

print()

print("Saved model to models/logistic_regression.joblib")