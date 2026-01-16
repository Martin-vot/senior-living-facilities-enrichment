import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://profiles.health.ny.gov/directory/acfs"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

facilities = []
for item in soup.find_all('div', class_='facility-item'):  # Uprav podle HTML struktury
    name = item.find('a').text.strip()
    address = item.find('p', class_='address').text.strip()
    facilities.append({'name': name, 'address': address})

df = pd.DataFrame(facilities)
df.to_csv('newyork_acf.csv', index=False)