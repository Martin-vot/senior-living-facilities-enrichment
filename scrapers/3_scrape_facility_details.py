import asyncio
from playwright.async_api import async_playwright
from asyncio import Semaphore
import openpyxl
import random
import csv
from urllib.parse import urlparse
from typing import List

INPUT_FILE = "../data/community_links.csv"
OUTPUT_FILE = "../data/facility_data.xlsx"
FAILED_URLS_FILE = "../data/failed_urls.csv"

CONCURRENCY = 3
BATCH_SIZE = 20
DELAY_BETWEEN_REQUESTS = (1, 3)  # min and max seconds

semaphore = Semaphore(CONCURRENCY)

# Read URLs from input file
def load_urls(filepath: str) -> List[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return [row[0] for row in reader]

# Save failed URLs
def save_failed_urls(failed_urls: List[str]):
    with open(FAILED_URLS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for url in failed_urls:
            writer.writerow([url])

# Check if the URL is valid
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# Scraping data from URL
async def extract_facility_data(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=random_user_agent())
            page = await context.new_page()

            await page.goto(url)

            try:
                name = await page.inner_text('.Facility_name')
            except:
                name = "Not available"

            try:
                address = await page.inner_text('.Facility_address')
            except:
                address = "Not available"

            # Splitting the adress
            address_parts = address.split(',')
            street = address_parts[0].strip() if len(address_parts) > 0 else "Not available"
            city = address_parts[1].strip() if len(address_parts) > 1 else "Not available"
            state_zip = address_parts[2].strip() if len(address_parts) > 2 else "Not available"
            state = state_zip.split(' ')[0] if state_zip != "Not available" else "Not available"
            zip_code = state_zip.split(' ')[1] if len(state_zip.split(' ')) > 1 else "Not available"

            # Types of facility
            try:
                care_type_elements = page.locator('.Facility__careTypeItem')
                care_types = await care_type_elements.all_text_contents()
                care_type = ", ".join(care_types) if care_types else "Not available"
            except:
                care_type = "Not available"

            # Phone number
            try:
                phone = await page.inner_text('.Facility_phone')
            except: 
                phone = "Not available"

            # Website url
            try:
                website = page.inner_text('.Facility_website')
            except:
                website = "Not available"

            # Desciption
            try:
                description = page.inner_text('.Facility_description')
            except:
                description = "Not available"

            await browser.close()

            return {
                "Facility Name": name,
                "Street Address": street,
                "City": city,
                "State": state,
                "Zip Code": zip_code,
                "Phone": phone,
                "Care Type": care_type,
                "Website": website,
                "Description": description
            }
    except Exception as e:
        log_failure(url, None, f"Unexpected error: {e}")
        return None
    
# Logging after every batch 
def log_failure(url, batch_id, reason):
    with open("failed_urls.csv", mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([url, batch_id if batch_id else "", reason])
    
# Generate a random user-agent string
def random_user_agent():
    agents = [
    # Chrome - Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

    # Firefox - Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",

    # Chrome - macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",

    # Firefox - macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.7; rv:120.0) Gecko/20100101 Firefox/120.0",

    # Safari - iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",

    # Chrome - Android
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",

    # Edge - Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
]

    return random.choice(agents)

async def main():
    urls = [url for url in load_urls(INPUT_FILE) if is_valid_url(url)]
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    headers_written = False

    async def process_url(url: str):
        async with semaphore:
            try:
                data = await extract_facility_data(url)
                if data:
                    nonlocal headers_written
                    if not headers_written:
                        sheet.append(list(data.keys()))
                        headers_written = True
                    sheet.append(list(data.values()))
                else:
                    save_failed_urls([url])
            except Exception as e:
                print(f"❌ Failed: {url} ({e})")
                save_failed_urls([url])
            await asyncio.sleep(random.uniform(*DELAY_BETWEEN_REQUESTS))

    async def process_batch(batch, batch_number):
        # Processing a batch and saving to a file after each batch
        tasks = [asyncio.create_task(process_url(url)) for url in batch]
        await asyncio.gather(*tasks)
        workbook.save(OUTPUT_FILE)
        print(f"✅ Batch {batch_number} uložen")

    # Splitting URLs into batches and parallelizing each batch
    for i in range(0, len(urls), BATCH_SIZE):
        current_batch = urls[i:i + BATCH_SIZE]
        await process_batch(current_batch, i // BATCH_SIZE + 1)

    print("✅ All URLs processed successfully.")


asyncio.run(main())