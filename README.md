# 🕷️ Large Scraper for Senior Living Facilities

This project is a robust, modular web scraping pipeline built with [Playwright](https://playwright.dev/) (both sync and async), designed to collect and enrich data on over 200,000 senior living facilities from [aplaceformom.com](https://www.aplaceformom.com/).

---

## 📁 Project Structure

```
Large-scraper/
├── scrapers/
│   ├── 1_parse_sitemap.py
│   ├── 2_extract_facility_links.py
│   ├── 3_scrape_facility_details.py
│   └── 4_enrich_with_google.py
├── data/
│   ├── facility_urls.csv
│   ├── community_links.csv
│   ├── facility_data.xlsx
│   ├── facility_data_enriched.xlsx
│   └── failed_urls.csv
```

---

## 🧠 How It Works

### 1️⃣ Parse Sitemap
`scrapers/1_parse_sitemap.py`  
- Downloads and parses the sitemap XML from the source website.
- Extracts URLs pointing to location-specific pages.
- Saves results to: `data/facility_urls.csv`

### 2️⃣ Extract Facility Links
`scrapers/2_extract_facility_links.py`  
- Opens each location URL from `facility_urls.csv`.
- Extracts individual facility page links.
- Saves results to: `data/community_links.csv`

### 3️⃣ Scrape Facility Details
`scrapers/3_scrape_facility_details.py`  
- Visits each facility URL from `community_links.csv`.
- Extracts:
  - Facility name
  - Address
  - Type (e.g., Assisted Living, Independent Living)
- Saves results to: `data/facility_data.xlsx`

### 4️⃣ Enrich with Google Search
`scrapers/4_enrich_with_google.py`  
- Uses Google search to find:
  - Phone number
  - Official website URL
- Takes names from `facility_data.xlsx`, enriches records.
- Saves enriched data to: `data/facility_data_enriched.xlsx`

---

## ⚙️ Features

✅ Built for **large-scale scraping** (200k+ URLs)  
✅ **User-Agent rotation** to avoid bans  
✅ **Batching, throttling, delays, and semaphores** for controlled concurrency  
✅ **Retry mechanism** via `data/failed_urls.csv`  
✅ Organized modular design (each step is restartable)  
✅ Playwright-powered with support for both **sync** and **async** flows  
✅ Data export in CSV and Excel formats

---

## 📦 Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt` (Playwright, pandas, openpyxl, etc.)

```bash
pip install -r requirements.txt
playwright install
```

---

## 🚀 Running the Pipeline

Run each step in order:

```bash
python scrapers/1_parse_sitemap.py
python scrapers/2_extract_facility_links.py
python scrapers/3_scrape_facility_details.py
python scrapers/4_enrich_with_google.py
```

You can re-run failed scrapes by processing the `failed_urls.csv`.

---

## 📊 Output

All output files are located in the `/data` directory:

| File                          | Description                                  |
|------------------------------|----------------------------------------------|
| `facility_urls.csv`          | URLs of city-specific facility listings      |
| `community_links.csv`        | URLs of individual facility pages            |
| `facility_data.xlsx`         | Raw scraped data (name, address, type)       |
| `facility_data_enriched.xlsx`| Enriched data (phone, website URL included)  |
| `failed_urls.csv`            | Failed requests for reprocessing             |

---

## 🧑‍💻 Author

**Martin Votava**  
GitHub: [martin-vot](https://github.com/martin-vot)  
Project ready for freelance or production use.

---

## 📝 License

This project is licensed under the MIT License.
