# 🎓 College Info AI Scraper Agent

An AI-powered agent to scrape detailed information about colleges including contacts, courses, placements, and more.

---

## 📋 What It Scrapes

| Field | Details |
|---|---|
| College Name | Full official name |
| Location | Address, city, state, pincode |
| Contact Number | Phone numbers |
| Email | Official email addresses |
| Principal Name | Head of institution |
| Courses | MBA, MCA, BCA, BE, BTech, Diploma |
| Placement Details | Top recruiters, avg/highest salary, placement % |
| Affiliation | University / Board |
| Website | Official URL |

---

## 🛠️ Steps to Build the AI Agent

### Step 1: Set Up Environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### Step 2: Configure API Keys
- Copy `config/config.example.env` → `config/.env`
- Add your **Groq API key** (free) OR **OpenAI API key**
- Optionally add **SerpAPI key** for Google search

### Step 3: Understand the Agent Architecture
```
main.py
 └── agents/
      └── college_agent.py       ← AI orchestrator (decides what to scrape)
 └── scrapers/
      ├── google_search.py       ← Finds college URLs via search
      ├── college_scraper.py     ← Scrapes individual college pages
      └── directory_scraper.py   ← Scrapes college directories (Shiksha, Collegedunia)
 └── utils/
      ├── data_cleaner.py        ← Cleans/normalizes extracted data
      ├── exporter.py            ← Saves to CSV/JSON/Excel
      └── logger.py              ← Logging utility
 └── output/                     ← Results saved here
```

### Step 4: Run the Agent
```bash
# Scrape colleges by city
python main.py --city "Bengaluru" --courses MBA,MCA,BCA

# Scrape colleges by state
python main.py --state "Karnataka" --courses BE,BTech,Diploma

# Scrape from a specific directory site
python main.py --source shiksha --city "Mumbai"

# Scrape with AI enrichment (fills missing fields via LLM)
python main.py --city "Pune" --ai-enrich
```

### Step 5: View Output
Results are saved to `output/` in:
- `colleges_data.csv` — spreadsheet format
- `colleges_data.json` — raw JSON
- `colleges_data.xlsx` — Excel with formatting

---

## 📦 Requirements
See `requirements.txt` for all dependencies.

## ⚠️ Legal Note
Use this tool responsibly. Always check a website's `robots.txt` and Terms of Service before scraping. Add delays between requests (`--delay 2`). For large-scale use, prefer official APIs or data partnerships.
