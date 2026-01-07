from playwright.sync_api import sync_playwright
import requests
import xml.etree.ElementTree as ET
import csv

# URL sitemapy
SITEMAP_URL = "https://www.example.com/sitemap-destination-pages.xml"

def fetch_sitemap(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def parse_sitemap(xml_data):
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    root = ET.fromstring(xml_data)
    urls = [url.find('ns:loc', ns).text for url in root.findall('ns:url', ns)]
    return urls

def save_to_csv(urls, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL'])
        for url in urls:
            writer.writerow([url])

if __name__ == "__main__":
    print("Downloading sitemap...")
    xml_data = fetch_sitemap(SITEMAP_URL)
    print("Parsing URL...")
    urls = parse_sitemap(xml_data)
    print(f"Found {len(urls)} URL.")
    save_to_csv(urls, "facility_urls.csv")
    print("Saved to 'facility_urls.csv'")
