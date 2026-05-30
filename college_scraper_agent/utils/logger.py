"""
utils/logger.py - Rich console logger
"""

from rich.console import Console
from rich.theme import Theme
import sys

custom_theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "scraping": "magenta",
})

console = Console(theme=custom_theme)


def log_info(msg: str):
    try:
        console.print(f"[info]ℹ  {msg}[/info]")
    except Exception:
        # Fallback for environments that can't render fancy characters
        print(f"INFO: {msg}", file=sys.stdout)

def log_success(msg: str):
    try:
        console.print(f"[success]✔  {msg}[/success]")
    except Exception:
        print(f"SUCCESS: {msg}", file=sys.stdout)

def log_warning(msg: str):
    try:
        console.print(f"[warning]⚠  {msg}[/warning]")
    except Exception:
        print(f"WARNING: {msg}", file=sys.stderr)

def log_error(msg: str):
    try:
        console.print(f"[error]✖  {msg}[/error]")
    except Exception:
        print(f"ERROR: {msg}", file=sys.stderr)

def log_scraping(msg: str):
    try:
        console.print(f"[scraping]🔍 {msg}[/scraping]")
    except Exception:
        print(f"SCRAPING: {msg}", file=sys.stdout)
