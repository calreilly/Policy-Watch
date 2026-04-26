import pandas as pd
import numpy as np

combine = pd.read_csv('data/combine_data.csv')
drafts = pd.read_csv('data/draft_picks.csv')

print(f"Combine dataset size: {combine.shape}")
print(f"Combine drafted players (non-null draft_ovr): {combine['draft_ovr'].notnull().sum()}")
print(f"Avg combine participants per year: {combine['draft_year'].value_counts().mean()}")
missing_pct = combine.isnull().mean() * 100
print("Missing values in combine:\n", missing_pct[missing_pct > 0].sort_values(ascending=False))
