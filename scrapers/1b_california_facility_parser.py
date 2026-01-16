import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://www.cdss.ca.gov/inforesources/community-care-licensing/facility-search-welcome"
params = {"facilityType": "RCFE", "county": ""}  # Pro all counties
response = requests.get(base_url, params=params)
soup = BeautifulSoup(response.text, 'html.parser')

# Extrahuj tabulku (předpokládej class 'search-results')
table = soup.find('table', class_='search-results')
if table:
    df = pd.read_html(str(table))[0]  # Převeď tabulku přímo do DataFrame
    df.to_csv('california_rcfe.csv', index=False)
