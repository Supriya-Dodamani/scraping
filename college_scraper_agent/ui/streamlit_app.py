import sys
from pathlib import Path
import io
import json

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd

from agents.college_agent import CollegeScraperAgent
from utils.exporter import export_data


def run_scraper(scope, city, state, courses, max_colleges, delay):
    agent = CollegeScraperAgent()
    return agent.run(scope=scope, city=city, state=state, courses=courses, max_colleges=max_colleges, delay=delay)


def main():
    st.set_page_config(page_title="College Scraper", layout="wide")
    st.title("🎓 College Info AI Scraper Agent — UI")

    with st.sidebar.form(key="scrape_form"):
        scope = st.selectbox("Search scope", ["country", "state", "city"], index=0, format_func=lambda x: "India" if x == "country" else ("State" if x == "state" else "City"))
        city = ""
        state = ""
        if scope == "city":
            city = st.text_input("City", value="")
        elif scope == "state":
            state = st.text_input("State", value="")
        courses_text = st.text_input("Courses (comma-separated)", value="MBA,MCA,BCA,BE,BTech,Diploma")
        max_colleges = st.number_input("Max colleges", min_value=1, max_value=500, value=50)
        delay = st.number_input("Delay between requests (s)", min_value=0.0, max_value=30.0, value=2.0)
        run_button = st.form_submit_button("Run Scraper")

    st.info("Use the sidebar to set parameters and press 'Run Scraper'.")

    if run_button:
        courses = [c.strip() for c in courses_text.split(",") if c.strip()]
        with st.spinner("Discovering and scraping colleges..."):
            colleges = run_scraper(
                scope=scope,
                city=city,
                state=state,
                courses=courses,
                max_colleges=int(max_colleges),
                delay=float(delay)
            )

        if not colleges:
            st.warning("No colleges found or scraping failed.")
            return

        # Convert to DataFrame for display and downloads
        records = [c.to_flat_dict() for c in colleges]
        df = pd.DataFrame(records)

        st.success(f"Scraped {len(df)} colleges")
        st.dataframe(df)

        # Download buttons
        csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8")
        st.download_button("Download CSV", data=csv_bytes, file_name="colleges_data.csv", mime="text/csv")

        json_bytes = json.dumps([c.model_dump() for c in colleges], indent=2, ensure_ascii=False).encode("utf-8")
        st.download_button("Download JSON", data=json_bytes, file_name="colleges_data.json", mime="application/json")

        # Save to output folder using exporter
        if st.button("Save to output/ (CSV, JSON, XLSX)"):
            export_data(colleges, output_dir="output", formats="csv,json,xlsx")
            st.success("Exported to output/")


if __name__ == "__main__":
    main()
