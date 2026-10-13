from __future__ import annotations
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.scheme_graph.config import settings
from src.scheme_graph.scraper import crawl_same_domain
from src.scheme_graph.parser import page_to_record
from src.scheme_graph.graph_builder import ensure_schema, upsert_source_record

def main():
    print("This ingestion run stores source pages first; it does not infer scheme facts automatically.")
    print("Validate source_inspection.json and .env SOURCE_URLS before crawling.")
    pages = crawl_same_domain(list(settings.source_urls), max_pages=settings.max_pages)
    records = [r for p in pages if (r := page_to_record(p))]
    out = Path("data/processed/scraped_records.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(records)} source records to {out}")
    if not records:
        print("No usable pages found. Review redirects and official alternate sources; nothing was written to Neo4j.")
        return
    ensure_schema()
    for record in records:
        result = upsert_source_record(record)
        print("Stored source:", result["url"])
    print("Source records stored. Next, verify them in Neo4j Browser before adding scheme entities.")

if __name__ == "__main__":
    main()
