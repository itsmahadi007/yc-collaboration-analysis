# YC Collaboration Startups Scraper - Design

**Date:** 2026-03-11
**Goal:** Collect YC collaboration startup data for market research and job hunting

## Data Source

`yc-oss.github.io/api` - community-maintained YC dataset sourced from Algolia search index.
Pre-structured JSON, no scraping/browser automation needed.

## Scope

Fetch companies tagged with collaboration + related tags:

```
collaboration, team-collaboration, productivity,
remote-work, workflow-automation, documents
```

Configurable tag list - user can add/remove tags and re-run.

## Script: `yc_collaboration_scraper.py`

### Flow

1. Fetch tag JSON files from `https://raw.githubusercontent.com/yc-oss/api/main/tags/{tag}.json`
2. Deduplicate companies across tags (by company ID)
3. Fetch each company's individual API endpoint for founder info enrichment
4. Export to CSV + SQLite

### Output Files

- `data/yc_collaboration_companies.csv` - flat file for quick browsing/filtering
- `data/yc_collaboration.db` - SQLite database with `companies` and `founders` tables

### Company Table Columns

| Column | Source | Example |
|--------|--------|---------|
| id | id | 1234 |
| name | name | "HackPad" |
| one_liner | one_liner | "A realtime wiki" |
| long_description | long_description | Full description |
| website | website | "https://hackpad.com" |
| batch | batch | "Winter 2012" |
| status | status | Active / Inactive / Acquired |
| team_size | team_size | 51 |
| is_hiring | isHiring | true / false |
| location | all_locations | "San Francisco, CA" |
| industry | industry | "B2B" |
| subindustry | subindustry | "B2B -> Productivity" |
| tags | tags | ["Collaboration", "Enterprise"] |
| stage | stage | "Early" / "Growth" |
| regions | regions | ["United States"] |
| yc_url | url | YC company page |
| source_tags | derived | Which of our search tags matched |

### Founders Table Columns

| Column | Example |
|--------|---------|
| company_id | 1234 |
| founder_name | "John Doe" |
| founder_linkedin | URL (if available) |
| founder_title | "CEO" |

### Tech Constraints

- **Zero external dependencies** - stdlib only (urllib, json, csv, sqlite3)
- **Re-runnable** - overwrites output with fresh data on each run
- **Rate limiting** - small delay between individual company API calls to be polite
- **Python 3.8+** compatible

## Use Cases

- **Market research**: Filter by status, batch, team_size to spot trends
- **Job hunting**: Filter `is_hiring=true`, check websites, find founder LinkedIn profiles
- **Statistics**: Batch distribution, geography, survival rate, growth stages
