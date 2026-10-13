from __future__ import annotations
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def inspect_url(url: str, timeout_ms: int = 30000) -> dict:
    """Inspect one URL and return visible text, final URL, status, title and links."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        response = None
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except PlaywrightTimeoutError:
                pass
            title = page.title()
            text = page.locator("body").inner_text(timeout=10000)
            links = page.locator("a[href]").evaluate_all(
                """els => els.map(a => ({
                    text: (a.innerText || a.getAttribute('aria-label') || '').trim(),
                    href: a.href
                })).filter(x => x.href)"""
            )
            return {
                "requested_url": url,
                "final_url": page.url,
                "status": response.status if response else None,
                "title": title,
                "text": text[:100000],
                "links": links,
            }
        finally:
            browser.close()

def crawl_same_domain(start_urls: list[str], max_pages: int = 10) -> list[dict]:
    """Small, bounded crawl. It does not bypass access controls or crawl off-domain."""
    queue = list(dict.fromkeys(start_urls))
    visited: set[str] = set()
    results: list[dict] = []
    allowed_hosts = {urlparse(u).netloc.lower() for u in start_urls}
    while queue and len(results) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            item = inspect_url(url)
        except Exception as exc:
            results.append({"requested_url": url, "error": str(exc), "links": [], "text": ""})
            continue
        results.append(item)
        final_host = urlparse(item.get("final_url", url)).netloc.lower()
        for link in item.get("links", []):
            target = link.get("href", "").split("#")[0]
            if not target or urlparse(target).scheme not in ("http", "https"):
                continue
            host = urlparse(target).netloc.lower()
            if host in allowed_hosts and target not in visited and target not in queue:
                # Avoid obvious non-content actions and assets.
                if not any(target.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".css", ".js", ".zip")):
                    queue.append(target)
    return results
