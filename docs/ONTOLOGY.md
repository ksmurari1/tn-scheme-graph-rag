# Knowledge Graph Ontology

## Implemented ontology

The current loaded Neo4j graph is deliberately small.

| Label / relationship | Role |
|---|---|
| `Department` | Department or agency category from the captured portal data |
| `Scheme` | A normalized scheme record |
| `(:Department)-[:OFFERS]->(:Scheme)` | Connects a department category to a scheme record |

The current snapshot contains 8 Department nodes, 123 Scheme nodes, and 123 `OFFERS` relationships.

## Scheme properties

The loaded Scheme nodes include properties corresponding to the normalized record, such as:

- `scheme_key` — composite key used by the loader
- `scheme_id`
- `name` and `name_tamil`
- department code/name metadata
- `year`
- `active` and `delete_status`
- `description` and `description_tamil`
- `eligibility` and `eligibility_tamil`
- `required_documents` and `required_documents_tamil`
- input/guideline metadata and source URL

Use the actual loader and normalized JSON as the source of truth for exact property names.

## Query-specific visualization

The query-focused graph adds a visualization-only root node for the user's question and connects it to the Scheme nodes retrieved for that question. These query-to-scheme edges are not stored ontology relationships. Stored Department-to-Scheme edges remain the factual graph relationships.

## Proposed future ontology

The following entities may be introduced after structured extraction and source verification:

| Proposed label | Intended meaning |
|---|---|
| `Source` | A provenance-bearing official page or document |
| `Beneficiary` | Beneficiary group explicitly stated in evidence |
| `Benefit` | Benefit or assistance explicitly stated in evidence |
| `Eligibility` | Eligibility condition explicitly stated in evidence |
| `Document` | Required document explicitly stated in evidence |

Potential relationships include `SUPPORTED_BY`, `MAY_BENEFIT`, `OFFERS_BENEFIT`, and `HAS_ELIGIBILITY`. These are proposals, not claims about the current database.

## Provenance and verification rules

- Do not infer eligibility, subsidy values, application dates, or required documents from a title alone.
- Preserve source text and source URL where available.
- Distinguish captured data from independently verified current facts.
- Before adding separate entity nodes, validate extraction against source text and retain evidence excerpts and verification timestamps.
- Do not describe the graph as authoritative until the source facts and evaluation set have been reviewed.
