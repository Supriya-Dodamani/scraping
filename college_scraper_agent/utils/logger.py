"""
utils/logger.py - Rich console logger
"""

from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "scraping": "magenta",
})

console = Console(theme=custom_theme)


def log_info(msg: str):
    console.print(f"[info]ℹ  {msg}[/info]")

def log_success(msg: str):
    console.print(f"[success]✔  {msg}[/success]")

def log_warning(msg: str):
    console.print(f"[warning]⚠  {msg}[/warning]")

def log_error(msg: str):
    console.print(f"[error]✖  {msg}[/error]")

def log_scraping(msg: str):
    console.print(f"[scraping]🔍 {msg}[/scraping]")
