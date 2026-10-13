
import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://www.tnagrisnet.tn.gov.in/home/schemes/en"

DEPARTMENTS = {
    "A": "Agriculture",
    "H": "Horticulture",
    "E": "Agricultural Engineering",
    "SO": "Seed Certification & Organic Certification",
    "M": "Marketing & Agri Business",
    "S": "Sugarcane",
    "T": "Tamil Nadu Watershed Development Agency",
    "TU": "Tamil Nadu Agricultural University",
}


async def print_options(page, select_id):
    select = page.locator(f"select#{select_id}")
    options = select.locator("option")
    results = []

    for i in range(await options.count()):
        option = options.nth(i)
        label = (await option.inner_text()).strip()
        value = await option.get_attribute("value")

        if value:
            results.append((label, value))

    print(f"\n{select_id}: {len(results)} options")

    for label, value in results[:30]:
        print(f"  - {label} [value={value}]")

    if len(results) > 30:
        print(f"  ... and {len(results) - 30} more")

    return results


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        requests_seen = []
        api_responses = []

        # Capture requests made by the page.
        page.on(
            "request",
            lambda request: requests_seen.append(
                (request.method, request.resource_type, request.url)
            )
            if request.resource_type in ("xhr", "fetch")
            else None,
        )

        # Capture responses from scheme-related endpoints.
        async def capture_response(response):
            if "Scheme_master/" not in response.url:
                return

            try:
                body = await response.text()

                api_responses.append({
                    "url": response.url,
                    "status": response.status,
                    "body": body,
                })

            except Exception as exc:
                api_responses.append({
                    "url": response.url,
                    "status": response.status,
                    "error": str(exc),
                })

        page.on(
            "response",
            lambda response: asyncio.create_task(
                capture_response(response)
            ),
        )

        await page.goto(URL, wait_until="domcontentloaded")
        await page.locator("select#dept").wait_for()
        await page.wait_for_timeout(2000)

        print("Page:", page.url)
        print("Title:", await page.title())

        await print_options(page, "dept")

        # Select each department and inspect the dependent dropdowns.
        for code, name in DEPARTMENTS.items():
            print(f"\n{'=' * 60}")
            print(f"Testing department: {name} ({code})")

            try:
                await page.locator("select#dept").select_option(code)
                await page.wait_for_timeout(2000)

                await print_options(page, "scheme_id")
                await print_options(page, "benifit_type")
                await print_options(page, "class_id")

            except Exception as exc:
                print(f"Could not inspect department: {exc}")

        print("\n" + "=" * 60)
        print("Background XHR / Fetch requests observed:")

        unique_requests = list(dict.fromkeys(requests_seen))

        for method, resource_type, url in unique_requests:
            print(f"{method} [{resource_type}] {url}")

        # Print captured API responses.
        print("\n" + "=" * 60)
        print("SCHEME API RESPONSE DETAILS")

        for index, item in enumerate(api_responses, start=1):
            print(f"\n--- Response {index} ---")
            print("URL:", item["url"])
            print("Status:", item["status"])

            if "body" in item:
                body = item["body"]
                print("Response characters:", len(body))
                print("Response preview:")
                print(body[:3000])

                # Attempt to identify whether the response is JSON.
                try:
                    parsed = json.loads(body)
                    print("Response format: Valid JSON")
                    if isinstance(parsed, (dict, list)):
                        print("Top-level type:", type(parsed).__name__)
                        if isinstance(parsed, dict):
                            print("Top-level keys:", list(parsed.keys()))
                except json.JSONDecodeError:
                    print("Response format: Not plain JSON")

            else:
                print("Capture error:", item.get("error"))

        # Save the captured responses for deeper inspection.
        with open(
            "data/processed/scheme_api_responses.json",
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                api_responses,
                file,
                ensure_ascii=False,
                indent=2,
            )

        print(
            "\nSaved API responses to "
            "data/processed/scheme_api_responses.json"
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
