import pandas as pd

url = "https://apps.hhs.texas.gov/providers/directories/AL.xlsx"
df = pd.read_excel(url)  # Přímé čtení z URL
df.to_csv('texas_alf.csv', index=False)  # Ulož jako CSV pro tvůj pipeline