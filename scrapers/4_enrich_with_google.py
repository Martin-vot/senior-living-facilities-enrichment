import pandas as pd
import asyncio
import random
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Load the data
INPUT_FILE = pd.read_excel("../data/facility_data.xlsx")
names = INPUT_FILE.iloc[:, 0]  # Facility names
phones = []
websites = []

CONCURRENCY = 3
BATCH_SIZE = 20
DELAY_BETWEEN_REQUESTS = (1, 3)


def extract_phone(text):
    match = re.search(r"(\+1\s?)?(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})", text)
    return match.group() if match else None


async def enrich_one(playwright, semaphore, query):
    async with semaphore:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random_user_agent())
        page = await context.new_page()
        try:
            await page.goto("https://www.google.com", timeout=10000)
            try:
                await page.click('button:has-text("Accept")', timeout=3000)
            except:
                pass

            await page.fill("input[name='q']", query)
            await page.keyboard.press("Enter")
            await page.wait_for_selector("h3", timeout=10000)

            snippets = await page.locator("div.VwiC3b").all_text_contents()
            links = page.locator("a")
            link_elements = await links.element_handles()
            first_link = None
            for a in link_elements:
                href = await a.get_attribute("href")
                if href and href.startswith("http") and "google.com" not in href:
                    first_link = href
                    break

            full_text = "\n".join(snippets)
            phone = extract_phone(full_text)

            return phone, first_link
        except PlaywrightTimeoutError:
            return None, None
        except Exception as e:
            print(f"Error during query '{query}': {e}")
            return None, None
        finally:
            await browser.close()
            await asyncio.sleep(random.uniform(*DELAY_BETWEEN_REQUESTS))

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

async def process_batch(batch, semaphore, playwright):
    tasks = []
    for name in batch:
        query = f"{name} phone site"
        tasks.append(enrich_one(playwright, semaphore, query))
    return await asyncio.gather(*tasks)


async def main():
    global phones, websites

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with async_playwright() as playwright:
        for i in range(0, len(names), BATCH_SIZE):
            batch = names[i:i + BATCH_SIZE]
            results = await process_batch(batch, semaphore, playwright)
            for phone, website in results:
                phones.append(phone)
                websites.append(website)
            print(f"Processed batch {i // BATCH_SIZE + 1}/{(len(names) + BATCH_SIZE - 1) // BATCH_SIZE}")

    # Assign enriched data
    INPUT_FILE.iloc[:, 5] = phones
    INPUT_FILE.iloc[:, 7] = websites
    INPUT_FILE.to_excel("../data/facility_data_enriched.xlsx", index=False)
    print("Enrichment complete. File saved as facility_data_enriched.xlsx")


if __name__ == "__main__":
    asyncio.run(main())
