# YC Collaboration Scraper - Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python script that fetches YC collaboration startups from yc-oss API, deduplicates, and exports to CSV + SQLite.

**Architecture:** Single script fetches JSON from GitHub-hosted API by tag, merges and deduplicates by company ID, then writes to CSV and SQLite. Zero external dependencies (stdlib only).

**Tech Stack:** Python 3.8+ stdlib (urllib, json, csv, sqlite3, time)

---

## File Structure

```
projects/yc-collaboration-analysis/
├── yc_scraper.py          # Main script - fetch, dedupe, export
├── data/                  # Output directory (gitignored)
│   ├── yc_collaboration_companies.csv
│   └── yc_collaboration.db
├── docs/
│   ├── design.md
│   └── plan.md
└── .gitignore
```

---

## Chunk 1: Core Script

### Task 1: Create .gitignore

**Files:**
- Create: `projects/yc-collaboration-analysis/.gitignore`

- [ ] **Step 1: Write .gitignore**

```
data/
__pycache__/
*.pyc
```

- [ ] **Step 2: Commit**

```bash
git add projects/yc-collaboration-analysis/.gitignore
git commit -m "chore(yc-scraper): add gitignore for data output"
```

---

### Task 2: Write the fetcher + deduplication logic

**Files:**
- Create: `projects/yc-collaboration-analysis/yc_scraper.py`

- [ ] **Step 1: Write the script with tag fetching and deduplication**

```python
#!/usr/bin/env python3
"""
YC Collaboration Startups Scraper

Fetches YC startups by tag from yc-oss.github.io/api,
deduplicates, and exports to CSV + SQLite.

Usage:
    python3 yc_scraper.py
    python3 yc_scraper.py --tags collaboration,productivity,remote-work
"""

import csv
import json
import os
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

BASE_URL = "https://raw.githubusercontent.com/yc-oss/api/main/tags"

DEFAULT_TAGS = [
    "collaboration",
    "team-collaboration",
    "productivity",
    "remote-work",
    "workflow-automation",
    "documents",
]

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

CSV_COLUMNS = [
    "id",
    "name",
    "one_liner",
    "long_description",
    "website",
    "batch",
    "status",
    "team_size",
    "is_hiring",
    "location",
    "industry",
    "subindustry",
    "tags",
    "stage",
    "regions",
    "yc_url",
    "source_tags",
]


def fetch_tag(tag: str) -> list[dict]:
    """Fetch companies for a single tag from yc-oss API."""
    url = f"{BASE_URL}/{tag}.json"
    print(f"  Fetching {tag}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "yc-scraper/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        print(f"    -> {len(data)} companies")
        return data
    except Exception as e:
        print(f"    -> FAILED: {e}")
        return []


def fetch_all(tags: list[str]) -> dict[int, dict]:
    """Fetch all tags and deduplicate by company ID."""
    companies = {}
    for tag in tags:
        entries = fetch_tag(tag)
        for entry in entries:
            cid = entry["id"]
            if cid in companies:
                companies[cid]["_source_tags"].add(tag)
            else:
                entry["_source_tags"] = {tag}
                companies[cid] = entry
        time.sleep(0.5)  # polite delay
    print(f"\nTotal unique companies: {len(companies)}")
    return companies


def normalize(company: dict) -> dict:
    """Normalize a company dict to flat CSV-friendly row."""
    return {
        "id": company.get("id"),
        "name": company.get("name", ""),
        "one_liner": company.get("one_liner", ""),
        "long_description": company.get("long_description", ""),
        "website": company.get("website", ""),
        "batch": company.get("batch", ""),
        "status": company.get("status", ""),
        "team_size": company.get("team_size", 0),
        "is_hiring": company.get("isHiring", False),
        "location": company.get("all_locations", ""),
        "industry": company.get("industry", ""),
        "subindustry": company.get("subindustry", ""),
        "tags": "; ".join(company.get("tags", [])),
        "stage": company.get("stage", ""),
        "regions": "; ".join(company.get("regions", [])),
        "yc_url": company.get("url", ""),
        "source_tags": "; ".join(sorted(company.get("_source_tags", set()))),
    }


def export_csv(rows: list[dict], path: Path):
    """Write rows to CSV."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV saved: {path} ({len(rows)} rows)")


def export_sqlite(rows: list[dict], path: Path):
    """Write rows to SQLite database."""
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(str(path))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE companies (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            one_liner TEXT,
            long_description TEXT,
            website TEXT,
            batch TEXT,
            status TEXT,
            team_size INTEGER,
            is_hiring BOOLEAN,
            location TEXT,
            industry TEXT,
            subindustry TEXT,
            tags TEXT,
            stage TEXT,
            regions TEXT,
            yc_url TEXT,
            source_tags TEXT
        )
    """)
    for row in rows:
        cur.execute(
            """
            INSERT INTO companies VALUES (
                :id, :name, :one_liner, :long_description, :website,
                :batch, :status, :team_size, :is_hiring, :location,
                :industry, :subindustry, :tags, :stage, :regions,
                :yc_url, :source_tags
            )
            """,
            row,
        )
    conn.commit()
    conn.close()
    print(f"SQLite saved: {path} ({len(rows)} rows)")


def main():
    tags = DEFAULT_TAGS
    if len(sys.argv) > 1 and sys.argv[1] == "--tags":
        tags = [t.strip() for t in sys.argv[2].split(",")]

    print(f"Tags: {', '.join(tags)}\n")

    companies = fetch_all(tags)
    rows = sorted(
        [normalize(c) for c in companies.values()],
        key=lambda r: r["name"].lower(),
    )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    export_csv(rows, DATA_DIR / "yc_collaboration_companies.csv")
    export_sqlite(rows, DATA_DIR / "yc_collaboration.db")

    # Quick stats
    active = sum(1 for r in rows if r["status"] == "Active")
    hiring = sum(1 for r in rows if r["is_hiring"])
    print(f"\nStats: {active} active, {hiring} hiring, {len(rows)} total")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script**

```bash
cd projects/yc-collaboration-analysis && python3 yc_scraper.py
```

Expected: Fetches 6 tags, prints company counts, saves CSV + SQLite, prints stats.

- [ ] **Step 3: Verify CSV output**

```bash
head -5 data/yc_collaboration_companies.csv
```

Expected: Header row + first 4 data rows with all columns populated.

- [ ] **Step 4: Verify SQLite output**

```bash
sqlite3 data/yc_collaboration.db "SELECT count(*) FROM companies;"
sqlite3 data/yc_collaboration.db "SELECT name, status, is_hiring FROM companies WHERE is_hiring = 1 LIMIT 5;"
```

Expected: Row count matches CSV, hiring companies listed.

- [ ] **Step 5: Test custom tags flag**

```bash
python3 yc_scraper.py --tags collaboration,remote-work
```

Expected: Only fetches 2 tags, smaller result set.

- [ ] **Step 6: Commit**

```bash
git add projects/yc-collaboration-analysis/yc_scraper.py
git commit -m "feat(yc-scraper): add scraper with CSV and SQLite export"
```
