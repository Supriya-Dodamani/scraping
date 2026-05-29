
import sys
import time
from pathlib import Path
from rich.console import Console

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scrapers.google_search import discover_college_urls
from scrapers.college_scraper import scrape_college_page

console = Console()


class CollegeScraperAgent:

    def __init__(self):
        pass

    def run(
        self,
        scope="country",
        city="",
        state="",
        courses=None,
        max_colleges=50,
        delay=2,
    ):

        if courses is None:
            courses = ["MBA", "MCA"]

        if scope == "country":
            location_label = "India"
            city = ""
            state = ""
        elif scope == "state":
            location_label = state or "India"
            city = ""
        else:
            location_label = city or "India"

        console.print(
            f"[cyan]🔍 Searching colleges in {location_label}[/cyan]"
        )

        urls = discover_college_urls(
            city=city,
            state=state,
            courses=courses,
            max_urls=max_colleges
        )

        console.print(
            f"[green]✅ Found {len(urls)} URLs[/green]"
        )

        urls = urls[:max_colleges]

        colleges = []

        for idx, url in enumerate(urls, start=1):

            console.print(
                f"[yellow]({idx}/{len(urls)}) Scraping:[/yellow] {url}"
            )

            try:

                data = scrape_college_page(url)

                if data:
                    colleges.append(data)

            except Exception as e:

                console.print(
                    f"[red]ERROR:[/red] {str(e)}"
                )

            time.sleep(delay)

        console.print(
            f"\n[bold green]✔ Scraped {len(colleges)} colleges[/bold green]"
        )

        return colleges

