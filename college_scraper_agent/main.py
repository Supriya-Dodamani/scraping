
import argparse
import sys
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

load_dotenv("config/.env")

console = Console()


# =========================================================
# Banner
# =========================================================
def print_banner():

    console.print(
        Panel.fit(
            "[bold cyan]🎓 College Info AI Scraper Agent[/bold cyan]\n"
            "[green]Google + Collegedunia + Shiksha Scraper[/green]\n"
            "[yellow]AI Powered College Discovery Engine[/yellow]",
            border_style="cyan",
        )
    )


# =========================================================
# Summary Table
# =========================================================
def print_summary(colleges):

    table = Table(
        title=f"Results — {len(colleges)} Colleges",
        show_lines=True
    )

    table.add_column(
        "College",
        style="bold cyan",
        max_width=35
    )

    table.add_column(
        "City",
        max_width=15
    )

    table.add_column(
        "Phone",
        max_width=18
    )

    table.add_column(
        "Email",
        max_width=30
    )

    table.add_column(
        "Website",
        max_width=35
    )

    table.add_column(
        "Status",
        max_width=10
    )

    for c in colleges[:50]:

        table.add_row(

            (c.name or "—")[:35],

            c.city or "—",

            c.phone_numbers[0] if c.phone_numbers else "—",

            c.emails[0] if c.emails else "—",

            (c.official_website or "—")[:35],

            c.scrape_status or "success"
        )

    console.print(table)


# =========================================================
# Main
# =========================================================
def main():

    print_banner()

    parser = argparse.ArgumentParser(
        description="College AI Scraper Agent"
    )

    parser.add_argument(
        "--scope",
        choices=["country", "state", "city"],
        default="country",
        help="Search scope: country (India), state, or city"
    )

    parser.add_argument(
        "--city",
        default="",
        help="City to scrape (used when --scope city)"
    )

    parser.add_argument(
        "--state",
        default="",
        help="State name (used when --scope state)"
    )

    parser.add_argument(
        "--courses",
        default="MBA,MCA,BCA,BE,BTech,Diploma",
        help="Comma separated courses"
    )

    parser.add_argument(
        "--max",
        type=int,
        default=100,
        help="Maximum colleges"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=2,
        help="Delay between requests"
    )

    parser.add_argument(
        "--output",
        default="output",
        help="Output folder"
    )

    args = parser.parse_args()

    # =========================================================
    # Parse Courses
    # =========================================================
    courses = [
        c.strip()
        for c in args.courses.split(",")
    ]

    if args.scope == "country":
        location_label = "India"
    elif args.scope == "state":
        location_label = args.state or "India"
    else:
        location_label = args.city or "India"

    console.print(
        f"[cyan]📍 Location:[/cyan] {location_label}"
    )

    console.print(
        f"[cyan]📚 Courses:[/cyan] {', '.join(courses)}"
    )

    # =========================================================
    # Run Agent
    # =========================================================
    try:

        from agents.college_agent import (
            CollegeScraperAgent
        )

        agent = CollegeScraperAgent()

        colleges = agent.run(
            scope=args.scope,
            city=args.city,
            state=args.state,
            courses=courses,
            max_colleges=args.max,
            delay=args.delay
        )

        # =========================================================
        # Summary
        # =========================================================
        print_summary(colleges)

        # =========================================================
        # Export
        # =========================================================
        from utils.exporter import export_data

        export_data(
            colleges,
            output_dir=args.output,
            formats="csv,json,xlsx"
        )

        console.print(
            "\n[bold green]✅ Export completed[/bold green]"
        )

    except KeyboardInterrupt:

        console.print(
            "\n[bold red]❌ Interrupted by user[/bold red]"
        )

    except Exception as e:

        console.print(
            f"\n[bold red]ERROR:[/bold red] {str(e)}"
        )

        sys.exit(1)


# =========================================================
# Start
# =========================================================
# Expose Flask `app` for platforms (like Vercel) that expect a top-level
# WSGI/Flask application variable named `app` in `main.py`.
try:
    # Import the Flask app if available. Keep it optional so CLI usage still works.
    from ui.flask_app import app  # type: ignore
except Exception:
    # If import fails, don't override CLI behavior; `app` will simply be absent.
    app = None  # type: ignore


if __name__ == "__main__":
    main()
