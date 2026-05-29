"""
utils/exporter.py - Export scraped college data to CSV, JSON, Excel
"""

import json
import os
from pathlib import Path
from typing import List

import pandas as pd

from models import CollegeInfo
from utils.logger import log_success, log_error


def export_data(colleges: List[CollegeInfo], output_dir: str = "output", formats: str = "csv,json,xlsx"):
    """Export list of CollegeInfo to specified formats."""
    os.makedirs(output_dir, exist_ok=True)
    flat_records = [c.to_flat_dict() for c in colleges]
    df = pd.DataFrame(flat_records)

    fmt_list = [f.strip().lower() for f in formats.split(",")]

    if "csv" in fmt_list:
        path = Path(output_dir) / "colleges_data.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        log_success(f"CSV saved → {path}")

    if "json" in fmt_list:
        path = Path(output_dir) / "colleges_data.json"
        raw = [c.model_dump() for c in colleges]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2, ensure_ascii=False)
        log_success(f"JSON saved → {path}")

    if "xlsx" in fmt_list:
        path = Path(output_dir) / "colleges_data.xlsx"
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Colleges")
            # Auto-fit columns
            ws = writer.sheets["Colleges"]
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)
        log_success(f"Excel saved → {path}")

    log_success(f"Total colleges exported: {len(colleges)}")
    return df
