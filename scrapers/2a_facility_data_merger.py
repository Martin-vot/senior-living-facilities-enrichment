import pandas as pd
from rapidfuzz import fuzz  # pip install rapidfuzz pro fuzzy match

# Načti tvůj dataset
your_df = pd.read_csv('your_50k_dataset.csv')

# Načti nové (např. Florida)
new_df = pd.read_csv('florida_alf.csv')

# Merge (outer join, odstran duplicity)
merged = pd.concat([your_df, new_df], ignore_index=True)
merged.drop_duplicates(subset=['address', 'name'], keep='first', inplace=True)

# Fuzzy clean-up (pokud adresa skoro shodná)
def is_duplicate(row1, row2):
    return fuzz.ratio(row1['address'], row2['address']) > 90

# Ulož
merged.to_csv('hybrid_dataset.csv', index=False)