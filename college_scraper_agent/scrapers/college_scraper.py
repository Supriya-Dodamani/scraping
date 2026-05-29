"""
scrapers/college_scraper.py
Scrapes individual college pages for detailed information.
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_fixed
from tenacity import RetryError
from requests.exceptions import RequestException, SSLError
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from models import CollegeInfo, CourseDetail, PlacementDetail
from utils.data_cleaner import (
    clean_phone, clean_email, clean_text,
    extract_salary_lpa, extract_percentage, normalize_course_name
)
from utils.logger import log_scraping, log_warning, log_error

TARGET_COURSES = {"MBA", "MCA", "BCA", "BE", "BTECH", "B.TECH", "B.E", "DIPLOMA"}
ua = UserAgent()


def get_headers():
    return {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }


# Configure a requests.Session with urllib3 Retry for better resilience
RETRY_STRATEGY = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"],
)
SESSION = requests.Session()
ADAPTER = HTTPAdapter(max_retries=RETRY_STRATEGY)
SESSION.mount("https://", ADAPTER)
SESSION.mount("http://", ADAPTER)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_page(url: str, timeout: int = 30) -> Optional[BeautifulSoup]:
    """Fetch a web page and return BeautifulSoup object using a resilient session."""
    try:
        resp = SESSION.get(url, headers=get_headers(), timeout=timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except SSLError as e:
        log_warning(f"SSL error for {url}: {e}. Retrying with verify=False.")
        try:
            resp = SESSION.get(url, headers=get_headers(), timeout=timeout, verify=False)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "lxml")
        except RequestException as inner_e:
            log_warning(f"SSL fallback failed for {url}: {inner_e}")
            raise
    except RequestException as e:
        log_warning(f"Fetch failed for {url}: {e}")
        raise
    except Exception as e:
        log_warning(f"Unexpected fetch error for {url}: {e}")
        raise


def extract_contact_info(soup: BeautifulSoup, college: CollegeInfo):
    """Extract phone numbers and emails from page."""
    full_text = soup.get_text(separator=" ")

    phones = clean_phone(full_text)
    emails = clean_email(full_text)

    college.phone_numbers = phones
    college.emails = emails


def extract_location(soup: BeautifulSoup, college: CollegeInfo):
    """Extract address and location details."""
    # Common patterns
    address_selectors = [
        {"itemprop": "address"},
        {"class": re.compile(r'address|location', re.I)},
        {"id": re.compile(r'address|location', re.I)},
    ]
    for sel in address_selectors:
        el = soup.find(attrs=sel)
        if el:
            college.address = clean_text(el.get_text())
            break

    # Try to find city/state from text patterns
    full_text = soup.get_text()
    # Pincode pattern
    pincode_match = re.search(r'\b(\d{6})\b', full_text)
    if pincode_match:
        college.pincode = pincode_match.group(1)


def extract_principal(soup: BeautifulSoup, college: CollegeInfo):
    """Extract principal / director name."""
    full_text = soup.get_text(separator="\n")
    patterns = [
        r'Principal\s*[:\-]?\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)',
        r'Director\s*[:\-]?\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)',
        r'Dean\s*[:\-]?\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)',
        r'HOD\s*[:\-]?\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)',
    ]
    for pat in patterns:
        m = re.search(pat, full_text)
        if m:
            college.principal_name = clean_text(m.group(1))
            break


def extract_courses(soup: BeautifulSoup, college: CollegeInfo):
    """Extract course details from the page."""
    full_text = soup.get_text(separator=" ").upper()
    found_courses = []
    found_names = []

    for course_key in TARGET_COURSES:
        if course_key in full_text:
            normalized = normalize_course_name(course_key)
            if normalized not in found_names:
                found_names.append(normalized)
                detail = CourseDetail(name=normalized)

                # Try to extract duration
                dur_pattern = rf'{course_key}.{{0,60}}(\d)\s*(?:Year|Yr)'
                dur_m = re.search(dur_pattern, full_text)
                if dur_m:
                    detail.duration = f"{dur_m.group(1)} Years"

                # Try to extract fees
                fee_pattern = rf'{course_key}.{{0,80}}(?:Rs\.?|INR|₹)\s*([\d,]+)'
                fee_m = re.search(fee_pattern, full_text)
                if fee_m:
                    fee_str = fee_m.group(1).replace(",", "")
                    try:
                        detail.fee_per_year = float(fee_str)
                    except:
                        pass

                found_courses.append(detail)

    college.courses = found_courses
    college.courses_offered_names = found_names


def extract_placements(soup: BeautifulSoup, college: CollegeInfo):
    """Extract placement information."""
    full_text = soup.get_text(separator=" ")
    placements = []

    for course in ["MBA", "MCA", "BCA", "BE", "BTech"]:
        pattern = rf'{course}.{{0,200}}(?:placement|placed|recruit)'
        section_match = re.search(pattern, full_text, re.IGNORECASE)
        if section_match:
            section = full_text[section_match.start():section_match.start() + 400]
            pd_obj = PlacementDetail(course=course)
            pd_obj.placement_percentage = extract_percentage(section)
            pd_obj.average_salary_lpa = extract_salary_lpa(section)

            # Top recruiters
            recruiter_pattern = r'(?:Infosys|TCS|Wipro|Accenture|HCL|IBM|Cognizant|Capgemini|Amazon|Google|Microsoft|Deloitte|KPMG|Flipkart|Zoho|Oracle)'
            recruiters = re.findall(recruiter_pattern, section, re.IGNORECASE)
            pd_obj.top_recruiters = list(set(recruiters))

            if any([pd_obj.placement_percentage, pd_obj.average_salary_lpa, pd_obj.top_recruiters]):
                placements.append(pd_obj)

    college.placements = placements


def extract_college_name(soup: BeautifulSoup) -> str:
    """Extract college name from page."""
    # Try og:title, h1, title tag
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return clean_text(og["content"])
    h1 = soup.find("h1")
    if h1:
        return clean_text(h1.get_text())
    return clean_text(soup.title.get_text()) if soup.title else ""


def scrape_college_page(url: str) -> CollegeInfo:
    """Main function: scrape a single college URL."""
    college = CollegeInfo(source_url=url)
    log_scraping(f"Scraping: {url}")

    try:
        soup = fetch_page(url)
        college.name = extract_college_name(soup)
        extract_contact_info(soup, college)
        extract_location(soup, college)
        extract_principal(soup, college)
        extract_courses(soup, college)
        extract_placements(soup, college)

        # Try to find official website link
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "official" in a.get_text().lower() or "website" in a.get_text().lower():
                college.official_website = href
                break

        # Affiliation
        full_text = soup.get_text()
        aff_match = re.search(r'(?:Affiliated to|Affiliation)\s*[:\-]?\s*([^\n\.]{5,60})', full_text, re.I)
        if aff_match:
            college.affiliation = clean_text(aff_match.group(1))

        # NAAC
        naac_match = re.search(r'NAAC\s*(?:Grade|Accredited)?\s*[:\-]?\s*([A-C]\+{0,2})', full_text, re.I)
        if naac_match:
            college.naac_grade = naac_match.group(1).upper()

        college.scrape_status = "success"
        log_scraping(f"✔ Done: {college.name or url}")

    except RetryError as e:
        college.scrape_status = "failed"
        college.scrape_errors.append(str(e))
        log_error(f"Failed to scrape {url} after retries: {e}")
    except Exception as e:
        college.scrape_status = "failed"
        college.scrape_errors.append(str(e))
        log_error(f"Failed to scrape {url}: {e}")

    return college
