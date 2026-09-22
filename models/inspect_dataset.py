import pandas as pd

df = pd.read_csv("data/processed/dataset.csv")

print("=" * 60)
print("Dataset shape")
print("=" * 60)

print(df.shape)

print()

print("=" * 60)
print("Columns")
print("=" * 60)

print(df.columns.tolist())

print()

print("=" * 60)
print("Missing values")
print("=" * 60)

print(df.isna().sum())

print()

print("=" * 60)
print("Winner distribution")
print("=" * 60)

print(df["winner"].value_counts())

print()

print("=" * 60)
print("First five rows")
print("=" * 60)

print(df.head())