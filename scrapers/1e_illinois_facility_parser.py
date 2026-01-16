import requests
from bs4 import BeautifulSoup
import pandas as pd

counties = ['cook', 'dupage', 'kane']  # Přidej víc
data = []
for county in counties:
    url = f"https://hfs.illinois.gov/medicalprograms/slf/{county}.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if table:
        df_county = pd.read_html(str(table))[0]
        data.append(df_county)

df = pd.concat(data)
df.to_csv('illinois_slp.csv', index=False)