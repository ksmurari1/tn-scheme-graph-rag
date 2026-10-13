from __future__ import annotations
import re
from urllib.parse import urlparse

def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def page_to_record(page: dict) -> dict | None:
    """Normalize a scraped page into a provenance-preserving source record."""
    if page.get("error") or not page.get("text"):
        return None
    text = clean_text(page["text"])
    title = clean_text(page.get("title", "")) or urlparse(page.get("final_url", "")).path
    if len(text) < 80:
        return None
    return {
        "title": title[:300],
        "url": page.get("final_url") or page.get("requested_url"),
        "text": text[:30000],
        "status": page.get("status"),
        "source_type": "official_web_page",
    }
