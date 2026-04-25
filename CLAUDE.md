# YC Collaboration Analysis

## Project Structure

```
yc-collaboration-analysis/
├── yc_scraper.py         # Scraper - fetches from yc-oss API, exports CSV + SQLite
├── notebooks/            # Analysis notebooks
│   ├── 00-dataset-info.ipynb     # Dataset overview, schema, freshness
│   ├── 01-overview.ipynb         # Stats, charts, search tool
│   ├── 02-trends-and-ideas.ipynb # Trends, business ideas, what earns more
│   └── 03-job-hunting.ipynb      # Hiring companies, search, shortlist export
├── data/                 # Output (gitignored)
│   ├── yc_collaboration_companies.csv
│   └── yc_collaboration.db
├── docs/
│   ├── design.md         # Original design spec
│   └── plan.md           # Implementation plan
├── pyproject.toml        # uv project config
└── CLAUDE.md             # This file
```

## Commands

```bash
# Install dependencies
uv sync

# Fetch all 5,690 YC companies
uv run python3 yc_scraper.py --all

# Fetch default collaboration tags only
uv run python3 yc_scraper.py

# Fetch custom tags
uv run python3 yc_scraper.py --tags ai,saas,developer-tools

# Launch notebooks
uv run jupyter lab notebooks/
```

## Data Source

All data comes from `yc-oss.github.io/api` (community-maintained, sourced from YC's Algolia index). The scraper uses only Python stdlib (urllib, json, csv, sqlite3) - no external packages needed for scraping.

## Database Schema

**Table: companies**

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | YC company ID |
| name | TEXT | Company name |
| one_liner | TEXT | Short description |
| long_description | TEXT | Full description |
| website | TEXT | Company URL |
| batch | TEXT | YC batch (e.g. "Winter 2024") |
| status | TEXT | Active / Inactive / Acquired |
| team_size | INTEGER | Employee count |
| is_hiring | BOOLEAN | Currently hiring |
| location | TEXT | HQ location |
| industry | TEXT | Primary industry |
| subindustry | TEXT | Sub-classification |
| tags | TEXT | Semicolon-separated tags |
| stage | TEXT | Early / Growth |
| regions | TEXT | Semicolon-separated regions |
| yc_url | TEXT | YC company page URL |
| source_tags | TEXT | Which search tags matched |

## Key Notes

- `data/` is checked into git - re-run scraper to refresh
- Scraper is re-runnable and idempotent (overwrites on each run)
- All notebooks live in `notebooks/` and read from `../data/` (relative path)
- New notebooks should follow naming: `NN-topic.ipynb`
- The `search()` function in `01-overview.ipynb` cell 10 is a reusable filter tool
