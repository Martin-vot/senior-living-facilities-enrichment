import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://quality.healthfinder.fl.gov/Facility-Search/FacilityLocateSearch"  # Add parameters for ALF type
response = requests.get(url, params={"type": "ALF"})  # edit params by form
soup = BeautifulSoup(response.text, 'html.parser')

# Find table with results (class 'facility-table' or similar)
rows = soup.find_all('tr', class_='result-row')
data = []
for row in rows:
    cols = row.find_all('td')
    if cols:
        name = cols[0].text.strip()
        address = cols[1].text.strip()
        phone = cols[2].text.strip()
        data.append({'name': name, 'address': address, 'phone': phone})

df = pd.DataFrame(data)
df.to_csv('florida_alf.csv', index=False)
