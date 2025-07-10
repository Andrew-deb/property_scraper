import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# --- Setup Selenium with robust crash‑prevention flags ---
options = Options()
options.headless = True

# these are important in Linux/container environments
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--single-process")

# optional but recommended
options.add_argument("--disable-extensions")
options.add_argument("--disable-background-timer-throttling")
options.add_argument("--disable-backgrounding-occluded-windows")
options.add_argument("--disable-renderer-backgrounding")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

BASE    = "https://www.finelib.com"
LISTING = BASE + "/cities/lagos/education/elementary-and-secondary-schools"
all_schools = []

for page in range(1, 13):
    url = f"{LISTING}/page-{page}" if page > 1 else LISTING
    print(f"→ Loading page {page}: {url}")
    driver.get(url)
    driver.implicitly_wait(5)
    soup = BeautifulSoup(driver.page_source, "lxml")

    for card in soup.select("a[href^='/business/']"):
        name = card.get_text(strip=True)
        if name.lower().startswith("write a review"):
            continue

        parent = card.parent
        addr   = parent.select_one("img[src*='loc.png']").next_sibling.strip()
        phones = parent.select_one("img[src*='phone.png']").next_sibling.strip()

        # follow detail link for email
        driver.get(BASE + card["href"])
        driver.implicitly_wait(3)
        detail_soup = BeautifulSoup(driver.page_source, "lxml")
        email_tag  = detail_soup.select_one("a[href^='mailto:']")
        email      = email_tag.get_text(strip=True) if email_tag else ""

        all_schools.append({
            "name":     name,
            "address":  addr,
            "contacts": phones,
            "email":    email
        })

driver.quit()

# Save to JSON and Excel
with open("lagos_schools.json", "w", encoding="utf-8") as f:
    json.dump(all_schools, f, ensure_ascii=False, indent=2)

pd.DataFrame(all_schools).to_excel("lagos_schools.xlsx", index=False)

print(f"✅ Scraped {len(all_schools)} schools; data saved.")
