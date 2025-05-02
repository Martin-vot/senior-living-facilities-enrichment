import asyncio
import csv
import random
import time
from typing import List
from playwright.async_api import async_playwright, Page
from asyncio import Semaphore
from urllib.parse import urlparse

INPUT_FILE = "../data/facility_urls.csv"
OUTPUT_FILE = "../data/community_links.csv"
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

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# Extract links from each city URL
async def scrape_community_links_from_city(playwright, city_url: str, writer, failed_urls: List[str]):
    async with semaphore:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random_user_agent())
        page = await context.new_page()

        try:
            if is_valid_url(city_url):
                await page.goto(city_url)
            else:
                print(f"Invalid URL: {city_url}")
            await page.goto(city_url, timeout=60000)
            await page.wait_for_selector(".CommunityCard", timeout=10000)
            cards = await page.locator(".CommunityCard h3 >> a").all()
            for card in cards:
                href = await card.get_attribute("href")
                if href:
                    full_url = "https://www.aplaceformom.com" + href
                    writer.writerow([full_url])
        except Exception as e:
            print(f"Failed for {city_url}: {e}")
            failed_urls.append(city_url)
        finally:
            await browser.close()
            await asyncio.sleep(random.uniform(*DELAY_BETWEEN_REQUESTS))

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

# Batch processing
async def process_batches(urls: List[str]):
    async with async_playwright() as playwright:
        for i in range(0, len(urls), BATCH_SIZE):
            batch = urls[i:i+BATCH_SIZE]
            print(f"Processing batch {i // BATCH_SIZE + 1}...")
            failed = []
            with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                tasks = [scrape_community_links_from_city(playwright, url, writer, failed) for url in batch]
                await asyncio.gather(*tasks)
            if failed:
                save_failed_urls(failed)

# Main entrypoint
if __name__ == "__main__":
    all_urls = load_urls(INPUT_FILE)
    asyncio.run(process_batches(all_urls))
