# 🏥 Senior Living Data Enrichment Pipeline

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Playwright](https://img.shields.io/badge/Playwright-Supported-green?style=for-the-badge&logo=playwright)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

A robust, modular web scraping and enrichment pipeline built with **Python** and **Playwright**. Designed to process **over 200,000+ senior living facility records** from publicly available senior living directories, automatically enriching them with validated contact information (direct phone numbers and websites).

![Pipeline Workflow](pipeline.png)

---

## 🚀 Key Features

*   **⚡ High-Volume Processing**: Capable of handling hundreds of thousands of records efficiently.
*   **🛡️ Anti-Blocking Architecture**: Implements User-Agent rotation, intelligent delays, and session management.
*   **🕹️ Full Concurrency Control**: Uses semaphores and throttling to balance speed with server load protocols.
*   **🔄 Resilient Logic**: Robust retry mechanisms for failed requests (`failed_urls.csv`) and fully restartable modular steps.
*   **📊 Clean Data Output**: Exports structured, analysis-ready data in CSV and Excel formats.

---

## 📁 Project Structure

```text
Senior-Living-Scraper/
├── scrapers/
│   ├── 1_parse_directory_index.py   # Parses public index/sitemaps for state/location links
│   ├── 2_extract_facility_links.py  # Extracts individual facility profile URLs
│   ├── 3_scrape_facility_details.py # Scrapes core facility data (Name, Address, Type)
│   └── 4_enrich_contacts.py         # Enriches records with Phone/Website via external verification
├── data/
│   ├── index_urls.csv
│   ├── facility_links.csv
│   ├── facility_data_enriched.xlsx  # Final output
│   └── failed_urls.csv
└── requirements.txt
```

---

## 🛠️ Workflows

### 1️⃣ Parse Directory Index
**`scrapers/1_parse_directory_index.py`**
Parses the main directory structure (e.g., sitemaps, state listings) to identify all relevant location pages.
*   **Output**: `data/index_urls.csv`

### 2️⃣ Extract Facility Links
**`scrapers/2_extract_facility_links.py`**
Iterates through location pages to collect specific profile URLs for every facility.
*   **Output**: `data/facility_links.csv`

### 3️⃣ Scrape Facility Details
**`scrapers/3_scrape_facility_details.py`**
Visits each facility profile to extract baseline data:
*   **Facility Name**
*   **Full Address & State**
*   **Care Types** (Assisted Living, Memory Care, etc.)
*   **Output**: `data/raw_facility_data.xlsx`

### 4️⃣ Enrich Contact Information
**`scrapers/4_enrich_contacts.py`**
Performs automated search and validation to append missing contact details:
*   **Direct Phone Number**
*   **Official Website URL**
*   **Output**: `data/enriched_facility_data.xlsx`

---

## 📊 Performance & Samples

The pipeline delivers high-accuracy enrichment metrics suitable for enterprise lead generation.

### Anonymized Sample Output

| Facility Name | Address | Care Type | Phone | Website |
| :--- | :--- | :--- | :--- | :--- |
| *Sample Community A* | *123 Oak St, Austin, TX* | Assisted Living | `+1 (512) 555-0123` | `www.sample-a.com` |
| *Sample Community B* | *456 Pine Ave, Denver, CO* | Memory Care | `+1 (303) 555-0199` | `www.sample-b.com` |
| *Sample Community C* | *789 Palm Dr, Miami, FL* | Independent Living | `+1 (305) 555-0155` | `www.sample-c.com` |

### Production Metrics (Demo Run)

> [!NOTE]
> Metrics based on a recent full-scale dataset execution.

| Metric | Result |
| :--- | :--- |
| **Total Facilities Processed** | **200,000+** |
| **Phone Enrichment Rate** | **~85–90%** |
| **Website Enrichment Rate** | **~75–85%** |
| **Pipeline Duration** | < 48 Hours |

---

## 📦 Getting Started

### Prerequisites

*   Python 3.9+
*   Playwright

### Installation

```bash
git clone https://github.com/your-username/senior-living-scraper.git
cd senior-living-scraper

pip install -r requirements.txt
playwright install
```

### Usage

Run the pipeline steps sequentially:

```bash
python scrapers/1_parse_directory_index.py
python scrapers/2_extract_facility_links.py
python scrapers/3_scrape_facility_details.py
python scrapers/4_enrich_contacts.py
```

---

## 🧑‍💻 About

**Martin Vot**  
*Europe-based Data Acquisition Specialist*

Specializing in high-volume web scraping, automated data enrichment, and ETL pipelines for complex datasets.

**Available for custom projects in:**  
🏥 Senior Living & Healthcare Data  
🏢 Real Estate Analytics  
📈 B2B Lead Generation  

[**🔗 LinkedIn**](https://www.linkedin.com/in/martin-vot-5377263a3/) &nbsp;|&nbsp; [**🌐 Website**](https://martin.vot.cz/)

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
