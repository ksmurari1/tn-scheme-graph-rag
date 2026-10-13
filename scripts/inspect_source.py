from __future__ import annotations
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.scheme_graph.config import settings
from src.scheme_graph.scraper import inspect_url

OUT = Path("data/processed/source_inspection.json")

def main():
    report = []
    for url in settings.source_urls:
        print(f"\nInspecting: {url}")
        try:
            result = inspect_url(url)
            print("Status:", result.get("status"))
            print("Final URL:", result.get("final_url"))
            print("Title:", result.get("title"))
            print("Text characters:", len(result.get("text", "")))
            print("Links found:", len(result.get("links", [])))
            print("\nText preview:\n", result.get("text", "")[:1200])
            print("\nFirst 15 links:")
            for link in result.get("links", [])[:15]:
                print("-", link.get("text", "")[:80], "->", link.get("href"))
            report.append(result)
        except Exception as exc:
            print("Inspection failed:", repr(exc))
            report.append({"requested_url": url, "error": str(exc)})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nInspection report saved to: {OUT}")

if __name__ == "__main__":
    main()
