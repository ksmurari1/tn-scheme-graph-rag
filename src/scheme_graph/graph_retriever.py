
from __future__ import annotations

import re

from src.scheme_graph.graph_builder import driver
from src.scheme_graph.config import settings


class SchemeGraphService:
    """Retrieval service for the SmartAgri AI Neo4j graph."""

    def _run(self, query: str, **params) -> list[dict]:
        with driver() as d:
            with d.session(database=settings.neo4j_database) as session:
                return [record.data() for record in session.run(query, **params)]

    def get_overview(self) -> dict:
        query = """
        OPTIONAL MATCH (d:Department)
        WITH count(d) AS departments
        OPTIONAL MATCH (s:Scheme)
        WITH departments, count(s) AS schemes
        OPTIONAL MATCH (:Department)-[r:OFFERS]->(:Scheme)
        RETURN departments, schemes, count(r) AS relationships
        """
        rows = self._run(query)
        return rows[0] if rows else {
            "departments": 0,
            "schemes": 0,
            "relationships": 0,
        }

    def get_graph(self, limit: int = 100) -> dict:
        rows = self._run("""
            MATCH (d:Department)-[r:OFFERS]->(s:Scheme)
            RETURN elementId(d) AS source_id,
                   d.name AS source_name,
                   type(r) AS relationship,
                   elementId(s) AS target_id,
                   s.name AS target_name
            ORDER BY d.name, s.name
            LIMIT $limit
        """, limit=max(1, min(limit, 500)))

        nodes, edges, seen = [], [], set()

        for row in rows:
            for node_id, name, group in [
                (row["source_id"], row["source_name"], "Department"),
                (row["target_id"], row["target_name"], "Scheme"),
            ]:
                if node_id not in seen:
                    seen.add(node_id)
                    nodes.append({
                        "id": node_id,
                        "label": str(name or "Unnamed")[:45],
                        "group": group,
                    })

            edges.append({
                "from": row["source_id"],
                "to": row["target_id"],
                "label": row["relationship"],
            })

        return {"nodes": nodes, "edges": edges}

    def get_query_graph(self, evidence: list[dict], question: str) -> dict:
        """Return one connected, query-focused graph for retrieved schemes.

        Department -> Scheme edges are read from Neo4j. The synthetic
        Query -> Scheme edges only mean "retrieved for this question"; they
        are visualization links, not stored domain relationships.
        """
        scheme_keys = list(dict.fromkeys(
            str(item.get("scheme_key"))
            for item in evidence
            if item.get("scheme_key") is not None
        ))
        if not scheme_keys:
            return {"nodes": [], "edges": []}

        rows = self._run("""
            MATCH (d:Department)-[r:OFFERS]->(s:Scheme)
            WHERE toString(s.scheme_key) IN $scheme_keys
            RETURN elementId(d) AS department_id,
                   d.name AS department_name,
                   type(r) AS relationship,
                   elementId(s) AS scheme_id,
                   s.scheme_key AS scheme_key,
                   s.name AS scheme_name,
                   s.year AS year,
                   s.active AS active
            ORDER BY d.name, s.name
        """, scheme_keys=scheme_keys)

        nodes, edges, seen = [], [], set()
        query_node_id = "smartagri-query-root"
        query_label = "Query: " + (question.strip() or "Your question")
        nodes.append({
            "id": query_node_id,
            "label": query_label[:48],
            "group": "Query",
            "title": (
                "Query focus node. Links to schemes mean they were retrieved "
                "for this question; they are not stored Neo4j domain relationships."
            ),
        })
        seen.add(query_node_id)

        linked_scheme_ids = set()
        for row in rows:
            department_id = row["department_id"]
            scheme_id = row["scheme_id"]

            if department_id not in seen:
                seen.add(department_id)
                nodes.append({
                    "id": department_id,
                    "label": str(row.get("department_name") or "Department")[:42],
                    "group": "Department",
                    "title": f"Department: {row.get('department_name') or 'Unknown'}",
                })

            if scheme_id not in seen:
                seen.add(scheme_id)
                scheme_name = str(row.get("scheme_name") or "Unnamed scheme")
                year = str(row.get("year") or "Year not specified")
                active = str(row.get("active") or "Not specified")
                nodes.append({
                    "id": scheme_id,
                    "label": scheme_name[:42],
                    "group": "Scheme",
                    "title": (
                        f"Scheme: {scheme_name}\\nYear: {year}\\n"
                        f"Source active flag: {active}"
                    ),
                })

            edges.append({
                "from": department_id,
                "to": scheme_id,
                "label": row["relationship"],
            })

            if scheme_id not in linked_scheme_ids:
                linked_scheme_ids.add(scheme_id)
                edges.append({
                    "from": query_node_id,
                    "to": scheme_id,
                    "label": "QUERY_MATCH",
                    "dashes": True,
                })

        return {"nodes": nodes, "edges": edges}

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {
            token for token in re.findall(r"[a-zA-Z0-9]+", text.lower())
            if len(token) > 1
        }

    
    def retrieve(self, question: str, limit: int = 8) -> list[dict]:
        """Retrieve relevant scheme evidence using topic filtering and weighted keywords."""
        question_tokens = self._tokens(question)
        if not question_tokens:
            return []

        rows = self._run("""
            MATCH (d:Department)-[:OFFERS]->(s:Scheme)
            WHERE coalesce(s.delete_status, 'no') <> 'yes'
            RETURN s.scheme_key AS scheme_key,
                   s.scheme_id AS scheme_id,
                   s.name AS name,
                   s.year AS year,
                   s.active AS active,
                   s.description AS description,
                   s.eligibility AS eligibility,
                   s.required_documents AS required_documents,
                   s.source_url AS source_url,
                   d.name AS department,
                   d.code AS department_code
        """)

        # Ignore common question words when identifying the requested topic.
        stop_words = {
            "which", "what", "where", "when", "who", "whom", "why",
            "how", "does", "do", "did", "is", "are", "was", "were",
            "the", "a", "an", "and", "or", "for", "to", "of", "in",
            "on", "with", "from", "by", "about", "mention", "mentions",
            "scheme", "schemes", "support", "supporting", "farmer",
            "farmers", "require", "requires", "required", "documents",
            "document", "eligible", "eligibility", "available"
        }
        topic_tokens = question_tokens - stop_words

        scored = []

        for row in rows:
            name = str(row.get("name") or "")
            description = str(row.get("description") or "")
            eligibility = str(row.get("eligibility") or "")
            documents = str(row.get("required_documents") or "")
            department = str(row.get("department") or "")

            name_tokens = self._tokens(name)
            description_tokens = self._tokens(description)
            eligibility_tokens = self._tokens(eligibility)
            document_tokens = self._tokens(documents)
            department_tokens = self._tokens(department)

            # If a specific topic is present, require it to appear in the
            # scheme name or its descriptive/eligibility evidence.
            searchable_topic_tokens = (
                name_tokens | description_tokens | eligibility_tokens
            )

            if topic_tokens and not (topic_tokens & searchable_topic_tokens):
                continue

            name_matches = question_tokens & name_tokens
            description_matches = question_tokens & description_tokens
            eligibility_matches = question_tokens & eligibility_tokens
            document_matches = question_tokens & document_tokens
            department_matches = question_tokens & department_tokens

            # Give scheme-name matches the highest weight.
            score = (
                4.0 * len(name_matches)
                + 1.5 * len(description_matches)
                + 1.5 * len(eligibility_matches)
                + 0.5 * len(document_matches)
                + 0.5 * len(department_matches)
            )

            # For a specific topic such as "cotton", prioritize records
            # whose scheme name itself contains that topic.
            if topic_tokens:
                name_topic_matches = topic_tokens & name_tokens
                evidence_topic_matches = topic_tokens & (
                    description_tokens | eligibility_tokens
                )

                if name_topic_matches:
                    score += 5.0 * len(name_topic_matches)
                elif evidence_topic_matches:
                    score += 1.0 * len(evidence_topic_matches)

            if score <= 0:
                continue

            evidence_parts = [
                f"Scheme: {name or 'Unknown'}",
                f"Department: {department or 'Unknown'}",
                f"Year: {row.get('year') or 'Not specified'}",
                f"Source active flag: {row.get('active') or 'Not specified'}",
            ]

            for label, value in [
                ("Description", description),
                ("Eligibility", eligibility),
                ("Required documents", documents),
            ]:
                if value:
                    evidence_parts.append(f"{label}: {value}")

            scored.append({
                "scheme_key": row.get("scheme_key"),
                "scheme_id": row.get("scheme_id"),
                "matched": name,
                "department": department,
                "year": row.get("year"),
                "active": row.get("active"),
                "score": round(score, 3),
                "source_url": row.get("source_url") or "",
                "evidence": "\n".join(evidence_parts),
            })

        # Ranking score is relative, not a confidence percentage.
        scored.sort(
            key=lambda item: (
                item["score"],
                item.get("active") == "yes",
            ),
            reverse=True,
        )

        return scored[:max(1, min(limit, 20))]
