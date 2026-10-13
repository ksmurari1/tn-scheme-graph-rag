# Data Sources and Ingestion

## Primary source

The project captured scheme records from the Tamil Nadu Agriculture Information and Management System (TNAgrIS) portal:

- Portal: https://www.tnagrisnet.tn.gov.in/home/schemes/en

The earlier government scheme-list URL used during exploration redirected to a generic homepage rather than a reliable scheme listing. The portal's scheme API responses were therefore inspected and captured. A URL or API response should not be assumed to be current or authoritative for a particular scheme without verification.

## Captured API categories

The project captured responses from these endpoint suffixes:

- `A` — Agriculture
- `H` — Horticulture
- `E` — Agricultural Engineering
- `SO` — Seed Certification & Organic Certification
- `M` — Marketing & Agri Business
- `S` — Sugarcane
- `T` — Tamil Nadu Watershed Development Agency
- `TU` — Tamil Nadu Agricultural University

The responses are saved in `data/processed/scheme_api_responses.json`. The normalized snapshot is saved in `data/processed/schemes_normalized.json`. `data/processed/source_inspection.json` records source-inspection information.

## Snapshot counts

The captured snapshot contains 123 records across 8 categories. These are counts from this project's files and must not be interpreted as the current total number of active schemes.

## Data fields

Captured fields include scheme identifiers, English and Tamil names, department names, year, active and deletion flags, descriptions, eligibility text, required-document text, input identifiers, guideline/document metadata, priority flag, and parent/main scheme identifier when present.

Normalization maps source fields into a consistent structure for loading and retrieval. Missing values should remain missing; do not invent them.

## Source and status caveats

- Records include historical and inactive entries.
- `active=yes` is a source field, not independent confirmation that applications are currently open.
- The `delete_status` flag is retained as source metadata; the default retrieval behavior excludes records marked deleted, but inactive historical records can still appear.
- The `source_url` currently points to a category API endpoint for many records, not a unique detail page for each scheme.
- The source snapshot may become stale and should be refreshed and revalidated before production use.

## Responsible ingestion

- Inspect the final URL and actual content returned before relying on a page.
- Preserve the source endpoint and available source metadata.
- Use bounded requests and respect the website's terms, access controls, and reasonable request rates.
- Keep raw inspection artifacts for debugging only when needed; do not commit secrets, session material, or unnecessary logs.
- Before refreshing the graph, review changes and understand whether the loader creates, updates, or replaces records.

## Future improvements

- Store a verified scheme-level source/detail URL when available.
- Record capture timestamps and verification status.
- Add provenance excerpts to evidence returned to the user.
- Introduce PDF, image, audio, or video extraction only when the source inventory requires it and the extraction results can be checked.
