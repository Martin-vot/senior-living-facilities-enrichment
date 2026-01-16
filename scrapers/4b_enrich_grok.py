import asyncio
import json
import re
from dotenv import load_dotenv
import os
import pandas as pd
from openai import AsyncOpenAI

# Set your xAI Grok API key (get from x.ai/api)
load_dotenv()
GROK_API_KEY = os.getenv("GROK_API_KEY")

if not GROK_API_KEY:
    raise ValueError("GROK_API_KEY not found in .env file!")

# Input and output files
INPUT_FILE = "3_data_facility_extracted/facility_data_test.xlsx"
OUTPUT_DIR = "4_data_enriched"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "facility_data_enriched.xlsx")

# Batch size for Grok calls
BATCH_SIZE = 5

# Grok client setup
client = AsyncOpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1"
)

def create_prompt(batch):
    facilities = []
    for i, (name, address) in enumerate(batch, 1):
        facilities.append(f"Facility {i}: Name: {name}, Address: {address}")
    
    prompt = f"""
You are a data extractor. For each senior living facility below, extract ONLY these fields from reliable public sources (prefer Google Business, official website, Yelp):

- phone: US format phone number (e.g. +1 512-555-0123 or 512-555-0123) or null
- website: full official website URL (starting with https:// or http://) or null
- rating: string in exact format "X.X / 5 from YYY reviews" (e.g. "4.3 / 5 from 127 reviews") or null if not found

Facilities:
{chr(10).join(facilities)}

Return ONLY a valid JSON array of objects in this exact order, nothing else:
[
  {{"phone": "... or null", "website": "... or null", "rating": "... or null"}},
  ...
]

Do NOT add explanations, introductions, conclusions or any other text.
"""
    return prompt

async def enrich_batch(batch, retry=True):
    prompt = create_prompt(batch)
    content = None
    try:
        response = await client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown code blocks if present
        if content.startswith("```"):
            content = re.sub(r"^```json\s*|^```\s*|```$", "", content, flags=re.MULTILINE).strip()
            
        data = json.loads(content)
        
        # Validate list length
        if isinstance(data, list) and len(data) == len(batch):
            return data
        else:
            print(f"Warning: Unexpected data length or format. Got {len(data) if isinstance(data, list) else 'type ' + str(type(data))}, expected {len(batch)}")
            if retry:
                print("Retrying batch...")
                return await enrich_batch(batch, retry=False)
            return [{} for _ in batch]
            
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error processing batch: {e}")
        if content:
            print(f"Content was: {content[:100]}...") # Print first 100 chars for debug
        else:
            print("Content was None (API call failed).")
            
        if retry:
            print("Retrying batch...")
            await asyncio.sleep(2)
            return await enrich_batch(batch, retry=False)
        return [{} for _ in batch]

async def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Reading input from {INPUT_FILE}...")
    try:
        df = pd.read_excel(INPUT_FILE)
    except FileNotFoundError:
        print(f"Input file not found: {INPUT_FILE}")
        return

    # Keep strictly columns 0-5
    df_base = df.iloc[:, :6].copy()
    
    # Ensure we use the correct columns for name and address (0 and 1)
    # Convert to list of tuples for processing
    rows_to_process = list(zip(df_base.iloc[:, 0].astype(str), df_base.iloc[:, 1].astype(str)))
    
    batches = [rows_to_process[i:i+BATCH_SIZE] for i in range(0, len(rows_to_process), BATCH_SIZE)]
    
    phones = []
    websites = []
    ratings = []
    
    print(f"Starting enrichment for {len(rows_to_process)} facilities...")
    
    for i, batch in enumerate(batches):
        print(f"Processing batch {i+1}/{len(batches)}...")
        enriched = await enrich_batch(batch)
        
        for item in enriched:
            phones.append(item.get('phone'))
            websites.append(item.get('website'))
            ratings.append(item.get('rating'))
            
        # Small delay to be nice to the API
        await asyncio.sleep(1)
    
    # Assign new columns. 
    # Logic: df_base has columns 0-5. 
    # New columns will be 6, 7, 8 in 0-indexed terms.
    df_base['Phone'] = phones
    df_base['Website'] = websites
    df_base['Rating'] = ratings
    
    # Save
    df_base.to_excel(OUTPUT_FILE, index=False)
    print(f"Enrichment complete. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())