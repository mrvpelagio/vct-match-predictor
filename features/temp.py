import pandas as pd

df = pd.read_csv("data/processed/dataset.csv")

print(df.iloc[20])
print()
print(df.iloc[100])