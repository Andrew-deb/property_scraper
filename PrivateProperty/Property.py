import asyncio
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, ProxyConfig
from crawl4ai.async_configs import CrawlerRunConfig

# ─── CONFIG ────────────────────────────────────────────────────────────────────
PROXY = ProxyConfig(
    server="brd.superproxy.io:33335",
    username="brd-customer-hl_1f8d9bef-zone-web_unlocker1",
    password="r5kcre6hey8j"
)
BROWSER_CFG = BrowserConfig(headless=True, proxy_config=PROXY)
RUN_CFG     = CrawlerRunConfig()

HOMEPAGE    = "https://www.property24.com.ng/"
OUTPUT_FILE = "all_states_output.md"
# ────────────────────────────────────────────────────────────────────────────────

async def get_state_links(crawler):
    """Fetch homepage and return a dict of {state_name: state_url_base}."""
    result = await crawler.arun(url=HOMEPAGE, config=RUN_CFG)
    soup   = BeautifulSoup(result.markdown, "html.parser")
    links  = {}
    for a in soup.find_all("a", href=True, text=True):
        href = a["href"]
        txt  = a.get_text(strip=True)
        # look only for links containing “for‑sale” (this filters to state pages)
        if "for-sale" in href:
            full = urljoin(HOMEPAGE, href)
            # remove any existing Page=… query
            base = re.sub(r"\?Page=\d+", "", full, flags=re.IGNORECASE)
            links[txt] = base
    return links

async def crawl_state(crawler, state_name, base_url, outfile):
    """Loop pages for one state until no markdown is returned."""
    page = 1
    while True:
        url = f"{base_url}?Page={page}"
        print(f"→ [{state_name}] fetching page {page}")
        try:
            res = await crawler.arun(url=url, config=RUN_CFG)
        except Exception as e:
            print(f"  ✖ error on {state_name} page {page}: {e}")
            break

        md = res.markdown.strip()
        if not md:
            print(f"  • no more listings for {state_name} at page {page}. stopping.")
            break

        # write out
        outfile.write(f"# {state_name} — Page {page}\n\n")
        outfile.write(md + "\n\n---\n\n")
        page += 1

async def main():
    async with AsyncWebCrawler(config=BROWSER_CFG) as crawler:
        # 1) grab all the state listing bases
        states = await get_state_links(crawler)
        print(f"Found {len(states)} states to scrape.")

        # 2) open our big output
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            # iterate each state
            for state_name, base_url in states.items():
                print(f"\n===> Starting {state_name}")
                await crawl_state(crawler, state_name, base_url, f)

    print(f"\n✅ Done! All listings written to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
