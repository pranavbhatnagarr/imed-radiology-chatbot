import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime

PROCEDURES = [
    {"name": "General X-Ray", "url": "https://i-med.com.au/procedures/general-x-ray"},
    {"name": "Lung Screening", "url": "https://i-med.com.au/procedures/lung-screening"},
    {"name": "Ultrasound", "url": "https://i-med.com.au/procedures/ultrasound"},
    {"name": "Cardiac Services", "url": "https://i-med.com.au/procedures/cardiac-services"},
    {"name": "MRI Scan", "url": "https://i-med.com.au/procedures/mri-scan"},
    {"name": "CT Scan", "url": "https://i-med.com.au/procedures/ct-scan"},
    {"name": "Mammography", "url": "https://i-med.com.au/procedures/mammography"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_page(name, url):
    try:
        print(f"Scraping {name}...")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove nav, footer, scripts, styles
        for tag in soup(["nav", "footer", "script", "style", "header"]):
            tag.decompose()

        # Get main content
        main = soup.find("main") or soup.find("article") or soup.find("div", class_=lambda x: x and "content" in x.lower())
        
        if main:
            text = main.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

        # Clean up blank lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        return {
            "name": name,
            "url": url,
            "content": clean_text,
            "scraped_at": datetime.now().isoformat(),
            "status": "success"
        }

    except requests.exceptions.Timeout:
        print(f"  ERROR: Timeout scraping {name}")
        return {"name": name, "url": url, "content": "", "status": "error", "error": "timeout"}

    except requests.exceptions.HTTPError as e:
        print(f"  ERROR: HTTP error scraping {name}: {e}")
        return {"name": name, "url": url, "content": "", "status": "error", "error": str(e)}

    except Exception as e:
        print(f"  ERROR: Unexpected error scraping {name}: {e}")
        return {"name": name, "url": url, "content": "", "status": "error", "error": str(e)}


def scrape_clinic_finder():
    url = "https://i-med.com.au/find-a-radiology-clinic"
    try:
        print(f"Scraping clinic finder...")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["nav", "footer", "script", "style", "header"]):
            tag.decompose()
        lines = [line.strip() for line in soup.get_text(separator="\n", strip=True).splitlines() if line.strip()]
        return "\n".join(lines)
    except Exception as e:
        return f"Error scraping clinic finder: {e}"


def main():
    results = []
    for procedure in PROCEDURES:
        result = scrape_page(procedure["name"], procedure["url"])
        results.append(result)
        time.sleep(1)  # Be polite to their servers

    # Save procedure data
    os.makedirs("data", exist_ok=True)
    with open("data/procedures.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} procedures to data/procedures.json")

    # Scrape and save clinic finder separately
    clinic_text = scrape_clinic_finder()
    with open("data/clinics_raw.txt", "w") as f:
        f.write(clinic_text)
    
    # Print Action Step 2 output
    lines = clinic_text.splitlines()
    print(f"\n--- ACTION STEP 2 OUTPUT ---")
    print(f"Total lines scraped: {len(lines)}")
    print(f"First 3 lines:")
    for line in lines[:3]:
        print(f"  {line}")

if __name__ == "__main__":
    main()