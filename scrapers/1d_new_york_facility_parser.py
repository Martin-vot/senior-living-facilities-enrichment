import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

url = "https://profiles.health.ny.gov/directory/acfs"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

facilities = []

# Find all listing divs
listings = soup.find_all('div', class_='listing')

for listing in listings:
    paragraphs = listing.find_all('p')
    
    if len(paragraphs) < 4:
        continue
        
    # Element 0: Facility Name (inside strong)
    facility_name = paragraphs[0].get_text(strip=True)
    
    # Element 1: Street Address
    street_address = paragraphs[1].get_text(strip=True)
    
    # Element 2: City, State Zip
    city_state_zip = paragraphs[2].get_text(strip=True)
    
    # Parse City, State, Zip
    # Default values
    city = ""
    state = ""
    zip_code = ""
    
    # Expected format: "City, State Zip"
    if ',' in city_state_zip:
        parts = city_state_zip.split(',')
        city = parts[0].strip()
        if len(parts) > 1:
            state_zip = parts[1].strip()
            # Split state and zip (usually separated by space)
            sz_parts = state_zip.split(' ')
            if len(sz_parts) >= 2:
                state = sz_parts[0]
                zip_code = sz_parts[1]
            else:
                state = state_zip # Fallback
                
    # Element 3: Phone
    phone_text = paragraphs[3].get_text(strip=True)
    phone = phone_text.replace("Tel:", "").strip()
    
    facilities.append({
        0: facility_name,
        1: street_address,
        2: city,
        3: state,
        4: zip_code,
        6: phone
    })

# Create DataFrame
# Specify columns up to 6 (Phone is at index 6, so we need 7 columns total: 0-6)
# We initialize all as None/Empty first
formatted_data = []

for f in facilities:
    row = [None] * 7
    row[0] = f[0]
    row[1] = f[1]
    row[2] = f[2]
    row[3] = f[3]
    row[4] = f[4]
    # Column 5 is empty
    row[6] = f[6]
    formatted_data.append(row)

df = pd.DataFrame(formatted_data)

# Save to Excel (no header as per implicit request for column indices, or standard headerless?
# Usually "column 0" implies the position. I will save without header to match the strict "column X" requirement cleanly, 
# or with a header if that's standard. The request says "Facility Name bude ve sloupci 0", 
# which usually refers to the data. I'll include headers for clarity but ensure position.
# Actually, precise column placement usually involves simply the data. I'll add headers for usability.
# Headers: Name, Address, City, State, Zip, Empty, Phone

columns = ["Facility Name", "Street Address", "City", "State", "Zip Code", "", "Phone"]
df.columns = columns

df.to_excel('newyork_acf.xlsx', index=False)
print("Data saved to newyork_acf.xlsx")
