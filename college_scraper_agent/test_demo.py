"""
test_demo.py - Quick demo that tests scraping a single college page
without needing any API keys.

Run: python test_demo.py
"""

from scrapers.college_scraper import scrape_college_page
from utils.exporter import export_data
from utils.logger import log_info, log_success

# Demo: scrape a publicly accessible college page
DEMO_URLS = [
    "https://www.rvce.edu.in",                   # RV College of Engineering, Bengaluru
    "https://www.pesuniversity.ac.in",            # PES University
    "https://www.msrit.edu",                      # MSRIT
]

def run_demo():
    log_info("Running demo scrape on sample college URLs...")
    colleges = []
    for url in DEMO_URLS:
        college = scrape_college_page(url)
        colleges.append(college)
        print(f"\n{'='*50}")
        print(f"Name        : {college.name}")
        print(f"Phones      : {college.phone_numbers}")
        print(f"Emails      : {college.emails}")
        print(f"Address     : {college.address}")
        print(f"Principal   : {college.principal_name}")
        print(f"Courses     : {college.courses_offered_names}")
        print(f"Affiliation : {college.affiliation}")
        print(f"NAAC        : {college.naac_grade}")
        print(f"Status      : {college.scrape_status}")

    export_data(colleges, output_dir="output", formats="csv,json,xlsx")
    log_success("Demo complete! Check the 'output/' folder.")

if __name__ == "__main__":
    run_demo()
