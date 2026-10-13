import json
from collections import Counter
from pathlib import Path

DATA_FILE = Path("data/processed/scheme_api_responses.json")


def main():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        responses = json.load(file)

    total_records = 0

    for response in responses:
        records = json.loads(response["body"])
        total_records += len(records)

        print("\n" + "=" * 65)
        print("Department:", response["url"].rsplit("/", 1)[-1])
        print("Total records:", len(records))

        print(
            "Active flags:",
            dict(Counter(str(r.get("active", "")) for r in records)),
        )
        print(
            "Delete flags:",
            dict(Counter(str(r.get("delete_status", "")) for r in records)),
        )

        print(
            "Records with description:",
            sum(bool(r.get("scheme_desc", "").strip()) for r in records),
        )
        print(
            "Records with eligibility:",
            sum(bool(r.get("eligibility", "").strip()) for r in records),
        )
        print(
            "Records with document requirements:",
            sum(bool(r.get("doc_req", "").strip()) for r in records),
        )

        print("First 3 scheme names:")
        for record in records[:3]:
            print(" -", record.get("Scheme_Name", "(unnamed)"))

    print("\n" + "=" * 65)
    print("TOTAL RECORDS ACROSS ALL DEPARTMENTS:", total_records)


if __name__ == "__main__":
    main()
