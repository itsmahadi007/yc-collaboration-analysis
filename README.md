# YC Collaboration Analysis

Scraper and dataset of Y Combinator startups for market research and job hunting.

## Data

- **5,690 companies** from the full YC directory
- Fields: name, description, website, batch, status, team size, hiring status, location, industry, tags, stage, regions, YC URL
- Source: [yc-oss/api](https://github.com/yc-oss/api)

## Setup

```bash
uv sync
```

## Scraper

```bash
# Fetch all YC companies
uv run python3 yc_scraper.py --all

# Fetch collaboration-related tags only (default)
uv run python3 yc_scraper.py

# Fetch custom tags
uv run python3 yc_scraper.py --tags ai,saas,developer-tools
```

Output goes to `data/` as CSV and SQLite.

## Analysis Notebooks

```bash
uv run jupyter lab notebooks/
```

### 01-overview.ipynb
Overview stats, charts, and search tool:
- Company status, hiring %, team size stats
- Companies by batch, top industries, geography
- Team size distribution, survival rate by year
- Most common tags, hiring companies, search & filter tool

### 02-trends-and-ideas.ipynb
Trends over time, business ideas, and what earns more:
- Tag trends over time (top 10 line chart)
- Fastest growing and declining tags (2023-2026 vs 2020-2022)
- Most common business niches (tag combinations)
- Team size by industry/sub-industry/tag (success proxy)
- Growth stage ratio by industry
- Survival rate by tag
- Composite score: best business ideas (trend + size + survival)

## SQL Queries

```sql
-- Companies currently hiring
SELECT name, website, batch, team_size FROM companies WHERE is_hiring = 1;

-- Companies by batch
SELECT batch, count(*) as cnt FROM companies GROUP BY batch ORDER BY cnt DESC;

-- Active companies by industry
SELECT industry, count(*) as cnt FROM companies WHERE status = 'Active' GROUP BY industry ORDER BY cnt DESC;

-- Large active hiring companies
SELECT name, website, team_size, location FROM companies
WHERE is_hiring = 1 AND status = 'Active' ORDER BY team_size DESC LIMIT 20;
```

## Dependencies

Managed via `uv`. Key packages:
- `pandas` - data analysis
- `matplotlib` - charts
- `jupyterlab` - interactive notebook
