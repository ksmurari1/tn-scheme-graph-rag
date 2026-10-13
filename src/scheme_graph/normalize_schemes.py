
import json
from pathlib import Path
from datetime import datetime, timezone

RAW_FILE = Path("data/processed/scheme_api_responses.json")
OUTPUT_FILE = Path("data/processed/schemes_normalized.json")

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


def clean(value):
    """Normalize text without inventing missing information."""
    if value is None:
        return ""
    return str(value).strip()


def normalize_record(record, department_code, source_url):
    return {
        "scheme_id": clean(record.get("scheme_id")),
        "scheme_name": clean(record.get("Scheme_Name")),
        "scheme_name_tamil": clean(record.get("Scheme_Name_Tamil")),
        "department_code": clean(record.get("dept")) or department_code,
        "department_name": DEPARTMENTS.get(
            clean(record.get("dept")) or department_code,
            clean(record.get("dept_tamil")) or "Unknown",
        ),
        "department_name_tamil": clean(record.get("dept_tamil")),
        "year": clean(record.get("year")),
        "active": clean(record.get("active")).lower(),
        "delete_status": clean(record.get("delete_status")).lower(),
        "description": clean(record.get("scheme_desc")),
        "description_tamil": clean(record.get("scheme_desc_tamil")),
        "eligibility": clean(record.get("eligibility")),
        "eligibility_tamil": clean(record.get("eligibility_tamil")),
        "required_documents": clean(record.get("doc_req")),
        "required_documents_tamil": clean(record.get("doc_req_tamil")),
        "input_ids": [
            item.strip()
            for item in clean(record.get("input_ids")).split(",")
            if item.strip()
        ],
        "guideline_document": clean(record.get("goUpload")),
        "priority_scheme": clean(record.get("priorityScheme")).lower(),
        "main_scheme_id": clean(record.get("mainSchemeId")),
        "source_url": source_url,
    }


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Raw API response file not found: {RAW_FILE}"
        )

    with RAW_FILE.open("r", encoding="utf-8") as file:
        responses = json.load(file)

    schemes = []
    seen_ids = set()

    for response in responses:
        source_url = response.get("url", "")
        body = response.get("body")

        if response.get("status") != 200 or not body:
            print(f"Skipping unsuccessful response: {source_url}")
            continue

        records = json.loads(body)

        if not isinstance(records, list):
            print(f"Skipping unexpected response format: {source_url}")
            continue

        department_code = source_url.rstrip("/").split("/")[-1]

        for record in records:
            normalized = normalize_record(
                record,
                department_code,
                source_url,
            )

            if not normalized["scheme_id"] or not normalized["scheme_name"]:
                continue

            # Scheme IDs may overlap between departments, so use both.
            unique_key = (
                normalized["department_code"],
                normalized["scheme_id"],
            )

            if unique_key in seen_ids:
                continue

            seen_ids.add(unique_key)
            schemes.append(normalized)

    schemes.sort(
        key=lambda item: (
            item["department_name"],
            item["scheme_name"].casefold(),
        )
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "metadata": {
            "project": "SmartAgri AI",
            "source": "Tamil Nadu Agriculture Department portal",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_response_count": len(responses),
            "normalized_scheme_count": len(schemes),
            "status_note": (
                "Status values are preserved from the source API; "
                "current scheme availability is not independently verified."
            ),
        },
        "schemes": schemes,
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    print("SmartAgri AI - Scheme Normalization")
    print("-" * 40)
    print("Source responses:", len(responses))
    print("Normalized schemes:", len(schemes))
    print("Departments represented:", len({
        scheme["department_code"] for scheme in schemes
    }))
    print("Output file:", OUTPUT_FILE)

    print("\nRecords by department:")
    department_counts = {}

    for scheme in schemes:
        name = scheme["department_name"]
        department_counts[name] = department_counts.get(name, 0) + 1

    for department, count in sorted(department_counts.items()):
        print(f"  {department}: {count}")

    print("\nData completeness:")
    for field, label in [
        ("description", "Description"),
        ("eligibility", "Eligibility"),
        ("required_documents", "Required documents"),
    ]:
        count = sum(bool(scheme[field]) for scheme in schemes)
        print(f"  {label}: {count}/{len(schemes)}")

    deleted = sum(
        scheme["delete_status"] == "yes" for scheme in schemes
    )
    active = sum(scheme["active"] == "yes" for scheme in schemes)

    print("\nSource status flags:")
    print("  Active = yes:", active)
    print("  Delete status = yes:", deleted)


if __name__ == "__main__":
    main()
