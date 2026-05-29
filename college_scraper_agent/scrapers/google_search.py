"""
scrapers/google_search.py
Finds college listing URLs using SerpAPI or raw Google search.
"""

import os
import time
import requests
from pathlib import Path
from typing import List
from urllib.parse import parse_qs, quote_plus, urlparse

from utils.logger import log_scraping, log_warning, log_info

# Load environment variables from config/.env when the module is imported.
# This helps the module work even if it is imported directly outside main.py.
try:
    from dotenv import load_dotenv
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    env_path = PROJECT_ROOT / "config" / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "2"))
if not SERPAPI_KEY:
    log_info("No SERPAPI_KEY configured — using direct search fallbacks (Google/DuckDuckGo).")


def search_colleges_serpapi(query: str, num_results: int = 10) -> List[str]:
    """Use SerpAPI to get Google search result URLs."""
    if not SERPAPI_KEY:
        return []

    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": num_results,
        "engine": "google",
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        urls = [r.get("link") for r in data.get("organic_results", []) if r.get("link")]
        return urls
    except Exception as e:
        log_warning(f"SerpAPI error: {e}")
        return []


def search_colleges_playwright(query: str, num_results: int = 10) -> List[str]:
    """Use Playwright to load Google search and extract result URLs."""
    try:
        from fake_useragent import UserAgent
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        log_warning(f"Playwright fallback unavailable: {e}")
        return []

    ua = UserAgent()
    encoded = quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}&num={num_results}&hl=en"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = browser.new_context(user_agent=ua.random, locale="en-US")
            page = context.new_page()
            page.goto(url, timeout=30000, wait_until="networkidle")
            page.wait_for_timeout(1500)
            anchors = page.query_selector_all('a[href^="/url?q="]')
            urls = []
            for a in anchors:
                href = a.get_attribute("href") or ""
                if href.startswith("/url?q="):
                    real = href.split("/url?q=")[1].split("&")[0]
                    if real.startswith("http") and "google" not in real:
                        urls.append(real)
                        if len(urls) >= num_results:
                            break
            context.close()
            browser.close()
            return urls
    except Exception as e:
        log_warning(f"Playwright Google scrape error: {e}")
        return []


def search_colleges_headers(query: str, num_results: int = 10) -> List[str]:
    """Scrape Google search results directly (fallback, may get blocked)."""
    from fake_useragent import UserAgent
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.google.com/",
    }
    encoded = quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}&num={num_results}&hl=en"

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")
        links = []
        for a in soup.select("a[href]"):
            href = a["href"]
            if href.startswith("/url?q="):
                real = href.split("/url?q=")[1].split("&")[0]
                if real.startswith("http") and "google" not in real:
                    links.append(real)
        if links:
            return links[:num_results]
        return search_colleges_duckduckgo(query, num_results=num_results)
    except Exception as e:
        log_warning(f"Google scrape error: {e}")
        return search_colleges_duckduckgo(query, num_results=num_results)


def search_colleges_duckduckgo(query: str, num_results: int = 10) -> List[str]:
    """Scrape DuckDuckGo HTML search results as a fallback."""
    from fake_useragent import UserAgent
    from bs4 import BeautifulSoup

    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://duckduckgo.com/",
    }
    encoded = quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, "lxml")
        links = []

        for a in soup.select("a.result__a"):
            href = a.get("href", "")
            real = ""
            if href.startswith("//duckduckgo.com/l/"):
                parsed = urlparse("https:" + href)
                params = parse_qs(parsed.query)
                real = params.get("uddg", [""])[0]
            elif href.startswith("http"):
                real = href

            if real and real.startswith("http") and "duckduckgo.com" not in real:
                links.append(real)
                if len(links) >= num_results:
                    break

        return links
    except Exception as e:
        log_warning(f"DuckDuckGo scrape error: {e}")
        return []


def build_college_queries(city: str = "", state: str = "",
                           courses: List[str] = None) -> List[str]:
    """Build targeted search queries for college discovery."""
    location = city or state or "India"
    courses = courses or ["MBA", "MCA", "BCA", "BE", "BTech", "Diploma"]
    course_str = " ".join(courses[:3])  # keep query concise

    queries = [
        f"colleges in {location} offering {course_str} site:shiksha.com",
        f"colleges in {location} offering {course_str} site:collegedunia.com",
        f"top engineering management colleges in {location} with placement details",
        f"MBA MCA BCA colleges in {location} contact email principal",
    ]
    return queries


def discover_college_urls(city: str = "", state: str = "",
                           courses: List[str] = None,
                           max_urls: int = 50) -> List[str]:
    """Main function to discover college page URLs."""
    queries = build_college_queries(city, state, courses)
    all_urls = []

    for q in queries:
        log_scraping(f"Searching: {q}")
        urls = search_colleges_serpapi(q, num_results=10)
        if not urls:
            urls = search_colleges_headers(q, num_results=10)
        if not urls:
            urls = search_colleges_duckduckgo(q, num_results=10)
        all_urls.extend(urls)
        time.sleep(REQUEST_DELAY)

    # Deduplicate
    seen = set()
    unique = []
    for u in all_urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)

    log_scraping(f"Discovered {len(unique)} unique URLs")
    return unique[:max_urls]
