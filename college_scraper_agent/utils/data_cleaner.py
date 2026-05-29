"""
utils/data_cleaner.py - Cleans and normalizes raw scraped data
"""

import re
from typing import List


def clean_phone(raw: str) -> List[str]:
    """Extract valid Indian phone numbers from raw text."""
    # Match 10-digit numbers, with optional country code
    pattern = r'(?:\+91[\s\-]?)?(?:[6-9]\d{9})'
    phones = re.findall(pattern, raw.replace(" ", "").replace("-", ""))
    # Normalize
    cleaned = []
    for p in phones:
        p = re.sub(r'\D', '', p)
        if p.startswith('91') and len(p) == 12:
            p = p[2:]
        if len(p) == 10:
            cleaned.append(p)
    return list(set(cleaned))


def clean_email(raw: str) -> List[str]:
    """Extract email addresses from raw text."""
    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, raw)
    return list(set(e.lower() for e in emails))


def clean_text(text: str) -> str:
    """Remove excess whitespace and non-printable characters."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def extract_salary_lpa(text: str) -> float | None:
    """Try to extract a salary figure in LPA from text."""
    # Matches: "12 LPA", "12.5 Lakhs", "12,00,000"
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:LPA|lpa|Lpa)',
        r'(\d+(?:\.\d+)?)\s*(?:lakhs?|Lakhs?)',
        r'(\d{1,2}),(\d{2}),(\d{3})',   # 12,00,000 format
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            if ',' in pat:
                # Convert 12,00,000 → 12 LPA approx
                num = int(m.group(1)) + int(m.group(2))/100
                return round(num, 2)
            return float(m.group(1))
    return None


def extract_percentage(text: str) -> float | None:
    """Extract percentage value from text."""
    m = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
    if m:
        return float(m.group(1))
    return None


def normalize_course_name(name: str) -> str:
    """Normalize course names to standard forms."""
    name = name.upper().strip()
    mapping = {
        'MASTER OF BUSINESS ADMINISTRATION': 'MBA',
        'MASTER OF COMPUTER APPLICATIONS': 'MCA',
        'BACHELOR OF COMPUTER APPLICATIONS': 'BCA',
        'BACHELOR OF ENGINEERING': 'BE',
        'BACHELOR OF TECHNOLOGY': 'BTech',
        'B.TECH': 'BTech',
        'B.E.': 'BE',
        'B.C.A': 'BCA',
        'M.B.A': 'MBA',
        'M.C.A': 'MCA',
    }
    return mapping.get(name, name)
