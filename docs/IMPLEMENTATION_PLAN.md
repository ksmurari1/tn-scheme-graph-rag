# Implementation Plan and Status

This document distinguishes the current working prototype from proposed enhancements. “Implemented” refers to the project state described in the current repository context; recheck the code before treating this as a release checklist.

## Phase 1 — Source inspection and capture

**Status: Implemented for the current snapshot**

- Inspected the official TNAgrIS scheme portal and its API responses.
- Captured eight department/category response sets.
- Saved source responses and inspection artifacts under `data/processed/`.
- Normalized the captured scheme records.

**Caveat:** The snapshot may be stale, and the generic government scheme-list URL redirected to a homepage during exploration.

## Phase 2 — Graph foundation

**Status: Implemented**

- Connected to Neo4j AuraDB.
- Loaded 8 Department nodes and 123 Scheme nodes.
- Created 123 `OFFERS` relationships.
- Added a graph overview and complete graph data path.

## Phase 3 — Retrieval and answer generation

**Status: Implemented prototype**

- Added weighted keyword retrieval over scheme metadata.
- Added an LLM answer service that receives retrieved evidence and is instructed not to invent missing facts.
- Displayed retrieved scheme evidence and source URL information in the UI.

**Known limitation:** Retrieval is not vector search or a full-text index. Relevance false positives are possible, and answer groundedness needs systematic evaluation.

## Phase 4 — Streamlit experience

**Status: Implemented prototype**

- Scheme Explorer.
- Ask SmartAgri AI.
- English/Tamil answer-language selection.
- Evidence display and source links.
- Complete graph visualization.
- Query-specific graph visualization with a query root and retrieved scheme nodes.
- Light-blue theme and improved text contrast.

## Phase 5 — Quality and provenance

**Status: Needs further work**

- Build and document a reviewed evaluation set.
- Test retrieval precision and false positives.
- Improve scheme-specific source links.
- Verify active status and current application availability against official sources.
- Add more robust provenance excerpts and capture/verification timestamps.
- Expand tests for English and Tamil questions.
- Validate behavior when evidence is missing.

## Phase 6 — Future enhancements

- Structured entity extraction with a validated schema.
- Separate Beneficiary, Benefit, Eligibility, Document, and Source nodes when source evidence supports them.
- Semantic/vector retrieval or a measured hybrid retrieval approach.
- Improved synonym and Tamil-language matching.
- More comprehensive automated tests and CI.
- Deployment hardening, monitoring, and secrets management.

## Completion principle

Only mark a capability complete after it exists in the repository and has been tested. Do not treat planned ontology nodes, semantic search, OCR, or multimodal ingestion as implemented until the corresponding code and evaluation evidence are available.
