# YC Collaboration Analysis

Scraper and dataset of Y Combinator startups for market research and job hunting.

## Data

- **5,690 companies** from the full YC directory
- Fields: name, description, website, batch, status, team size, hiring status, location, industry, tags, stage, regions, YC URL
- Source: [yc-oss/api](https://github.com/yc-oss/api)

## Usage

```bash
# Fetch all YC companies
python3 yc_scraper.py --all

# Fetch collaboration-related tags only (default)
python3 yc_scraper.py

# Fetch custom tags
python3 yc_scraper.py --tags ai,saas,developer-tools
```

Output goes to `data/` as CSV and SQLite.

## Example Queries

```sql
-- Companies currently hiring
SELECT name, website, batch, team_size FROM companies WHERE is_hiring = 1;

-- Companies by batch
SELECT batch, count(*) as cnt FROM companies GROUP BY batch ORDER BY cnt DESC;

-- Active companies by industry
SELECT industry, count(*) as cnt FROM companies WHERE status = 'Active' GROUP BY industry ORDER BY cnt DESC;

-- Large active hiring companies
SELECT name, website, team_size, location FROM companies WHERE is_hiring = 1 AND status = 'Active' ORDER BY team_size DESC LIMIT 20;
```

## Requirements

Python 3.8+ (stdlib only, no external dependencies).
