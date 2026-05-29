"""
scrapers/directory_scraper.py
Scrapes college listings from major Indian education directories:
- Shiksha.com
- Collegedunia.com
- CollegeDekho.com
"""

import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import List
from urllib.parse import urljoin

from models import CollegeInfo
from utils.logger import log_scraping, log_warning

ua = UserAgent()
DELAY = 2


def get_headers():
    return {"User-Agent": ua.random, "Accept-Language": "en-US,en;q=0.9"}


# ─── Shiksha.com ────────────────────────────────────────────────

def scrape_shiksha_listing(city: str, course: str = "mba", pages: int = 3) -> List[str]:
    """Get college detail page URLs from Shiksha listing."""
    urls = []
    course_map = {
        "MBA": "mba", "MCA": "mca", "BCA": "bca",
        "BE": "be", "BTech": "btech", "Diploma": "diploma-engineering"
    }
    course_slug = course_map.get(course.upper(), course.lower())
    city_slug = city.lower().replace(" ", "-")

    for page in range(1, pages + 1):
        url = f"https://www.shiksha.com/university-college/colleges/{course_slug}-colleges-in-{city_slug}"
        if page > 1:
            url += f"?page={page}"

        log_scraping(f"Shiksha listing page {page}: {url}")
        try:
            resp = requests.get(url, headers=get_headers(), timeout=20)
            soup = BeautifulSoup(resp.text, "lxml")
            # Shiksha college card links
            for a in soup.select("a[href*='/university-college/']"):
                href = a.get("href", "")
                if href and "/colleges/" not in href and href not in urls:
                    full = urljoin("https://www.shiksha.com", href)
                    urls.append(full)
            time.sleep(DELAY)
        except Exception as e:
            log_warning(f"Shiksha listing error: {e}")

    return list(set(urls))


def parse_shiksha_college(url: str) -> CollegeInfo:
    """Parse a Shiksha college detail page."""
    college = CollegeInfo(source_url=url)
    try:
        resp = requests.get(url, headers=get_headers(), timeout=20)
        soup = BeautifulSoup(resp.text, "lxml")

        # Name
        h1 = soup.find("h1")
        if h1:
            college.name = h1.get_text(strip=True)

        # Location
        loc = soup.find(class_=lambda c: c and "location" in c.lower())
        if loc:
            college.address = loc.get_text(strip=True)

        # Contact
        full_text = soup.get_text()
        from utils.data_cleaner import clean_phone, clean_email
        college.phone_numbers = clean_phone(full_text)
        college.emails = clean_email(full_text)

        college.scrape_status = "success"
    except Exception as e:
        college.scrape_status = "failed"
        college.scrape_errors.append(str(e))
    return college


# ─── Collegedunia.com ───────────────────────────────────────────

def scrape_collegedunia_listing(city: str, course: str = "mba", pages: int = 3) -> List[str]:
    """Get college URLs from Collegedunia listings."""
    urls = []
    course_map = {
        "MBA": "mba", "MCA": "mca", "BCA": "bca",
        "BE": "be-btech", "BTech": "be-btech", "Diploma": "diploma"
    }
    course_slug = course_map.get(course.upper(), course.lower())
    city_slug = city.lower().replace(" ", "-")

    for page in range(1, pages + 1):
        url = f"https://collegedunia.com/{course_slug}-colleges-in-{city_slug}"
        if page > 1:
            url += f"?page={page}"

        log_scraping(f"Collegedunia page {page}: {url}")
        try:
            resp = requests.get(url, headers=get_headers(), timeout=20)
            soup = BeautifulSoup(resp.text, "lxml")

            for a in soup.select("a[href]"):
                href = a.get("href", "")
                if "/university-college/" in href or "/colleges/" in href:
                    full = urljoin("https://collegedunia.com", href)
                    if full not in urls:
                        urls.append(full)
            time.sleep(DELAY)
        except Exception as e:
            log_warning(f"Collegedunia listing error: {e}")

    return list(set(urls))


# ─── Unified directory scraper ──────────────────────────────────

def get_college_urls_from_directories(
    city: str = "",
    courses: List[str] = None,
    sources: List[str] = None,
    pages_per_course: int = 2
) -> List[str]:
    """
    Aggregate college URLs from multiple directory sources.
    sources: list of 'shiksha', 'collegedunia'
    """
    courses = courses or ["MBA", "MCA", "BCA", "BE", "BTech"]
    sources = sources or ["shiksha", "collegedunia"]

    all_urls = []
    for source in sources:
        for course in courses:
            if source == "shiksha":
                urls = scrape_shiksha_listing(city, course, pages=pages_per_course)
            elif source == "collegedunia":
                urls = scrape_collegedunia_listing(city, course, pages=pages_per_course)
            else:
                urls = []
            log_scraping(f"[{source}] {course}: found {len(urls)} URLs")
            all_urls.extend(urls)

    unique = list(set(all_urls))
    log_scraping(f"Total unique college URLs from directories: {len(unique)}")
    return unique
