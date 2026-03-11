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
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

BASE_URL = "https://raw.githubusercontent.com/yc-oss/api/main/tags"
ALL_COMPANIES_URL = "https://raw.githubusercontent.com/yc-oss/api/main/companies/all.json"

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


def fetch_all_companies() -> dict[int, dict]:
    """Fetch the entire YC company dataset in one request."""
    print("  Fetching ALL companies...")
    try:
        req = urllib.request.Request(ALL_COMPANIES_URL, headers={"User-Agent": "yc-scraper/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        print(f"    -> {len(data)} companies")
        companies = {}
        for entry in data:
            entry["_source_tags"] = set(t.lower().replace(" ", "-") for t in entry.get("tags", []))
            companies[entry["id"]] = entry
        return companies
    except Exception as e:
        print(f"    -> FAILED: {e}")
        return {}


def main():
    use_all = "--all" in sys.argv

    if use_all:
        print("Mode: ALL companies\n")
        companies = fetch_all_companies()
    elif len(sys.argv) > 1 and sys.argv[1] == "--tags":
        tags = [t.strip() for t in sys.argv[2].split(",")]
        print(f"Tags: {', '.join(tags)}\n")
        companies = fetch_all(tags)
    else:
        print(f"Tags: {', '.join(DEFAULT_TAGS)}\n")
        companies = fetch_all(DEFAULT_TAGS)

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
