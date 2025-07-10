from typing import Type
from pydantic import BaseModel, Field
import asyncio
import os

from crawl4ai import AsyncWebCrawler, BrowserConfig, ProxyConfig
from crawl4ai.async_configs import CrawlerRunConfig

# Proxy and browser setup (same for all pages)
proxy_config = ProxyConfig(
    server="brd.superproxy.io:33335",
    username="brd-customer-hl_673bb827-zone-richard",
    password="stsx3kwkir9j"
)
browser_config = BrowserConfig(
    headless=True,
    proxy_config=proxy_config,
)
run_config = CrawlerRunConfig()

BASE_URL = "https://privateproperty.ng/property-for-sale"
START_PAGE = 3165
END_PAGE = 21064  # ← change this to the last page you want to scrape

async def crawl_pages(start: int, end: int, output_file: str):
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Open output file once, write as we go
        with open(output_file, "w", encoding="utf-8") as f:
            for page in range(start, end + 1):
                url = f"{BASE_URL}?Page={page}"
                print(f"Fetching page {page} → {url}")
                try:
                    result = await crawler.arun(url=url, config=run_config)
                    # Write a heading for each page
                    f.write(f"# Page {page}\n\n")
                    f.write(result.markdown)
                    f.write("\n\n---\n\n")
                except Exception as e:
                    print(f"⚠️  Failed to fetch page {page}: {e}")
    print(f"All pages {start}–{end} written to {output_file}")

if __name__ == "__main__":
    asyncio.run(crawl_pages(START_PAGE, END_PAGE, "private_property.md"))
