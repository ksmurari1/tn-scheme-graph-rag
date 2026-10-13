# Guardrails and Evaluation

## Purpose

Evaluation should establish whether SmartAgri AI retrieves relevant scheme records and generates answers that remain grounded in the retrieved evidence. The current project is a prototype; the evaluation checklist below is a plan unless results are explicitly recorded.

## Current behavior to validate

- Empty or irrelevant questions should be handled gracefully by the UI and retrieval flow.
- Retrieval ranks scheme records using weighted keyword matching.
- The ranking score is a relevance signal, not a calibrated confidence probability.
- LLM prompts instruct the model to use provided evidence and avoid inventing missing facts.
- The UI displays evidence and source URL information for user inspection.
- Historical and inactive records may be retrieved; status must not be described as currently available without verification.

These behaviors require tests; prompt instructions alone do not prove groundedness.

## Recommended evaluation set

Create a reviewed test set covering:

1. Scheme discovery by department.
2. Scheme discovery using a crop or topic, such as paddy or cotton.
3. Questions about required documents when evidence is present.
4. Questions where eligibility evidence is absent or incomplete.
5. Benefit or subsidy amount questions.
6. Application process and deadlines.
7. Ambiguous scheme names and broad topic terms.
8. Prompt injection and requests to expose secrets.
9. Questions unrelated to Tamil Nadu scheme information.
10. English and Tamil questions and answer-language selection.
11. Inactive or historical schemes.
12. Queries likely to produce keyword false positives.

## Metrics

- Retrieval relevance at top-k.
- Evidence coverage.
- Answer groundedness / unsupported-claim rate.
- Correct abstention when evidence is missing.
- Correct treatment of inactive or historical records.
- Source-link usefulness and scheme-level URL accuracy.
- English/Tamil answer quality.
- End-to-end latency and error rate.

## Known evaluation risks

- Keyword matching can miss synonyms and can return false positives when a topic word appears in broad descriptions.
- Generic API endpoint links are less useful than verified individual scheme detail links.
- A model can still generate unsupported statements despite strict prompt instructions.
- Source data may be stale or include inactive records.

## Release gate

Do not describe SmartAgri AI as an authoritative eligibility or scheme-status service until source facts have been verified against current official information, retrieval and answer tests have been run, and results have been documented.
