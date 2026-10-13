from __future__ import annotations
import hashlib
from neo4j import GraphDatabase
from src.scheme_graph.config import settings

SCHEMA = """
CREATE CONSTRAINT scheme_id IF NOT EXISTS FOR (s:Scheme) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT source_url IF NOT EXISTS FOR (s:Source) REQUIRE s.url IS UNIQUE;
CREATE CONSTRAINT department_name IF NOT EXISTS FOR (d:Department) REQUIRE d.name IS UNIQUE;
"""

def _id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]

def driver():
    if not (settings.neo4j_uri and settings.neo4j_username and settings.neo4j_password):
        raise RuntimeError("Configure NEO4J_URI, NEO4J_USERNAME and NEO4J_PASSWORD in .env.")
    return GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password))

def ensure_schema():
    with driver() as d:
        with d.session(database=settings.neo4j_database) as session:
            for statement in SCHEMA.strip().split(";"):
                if statement.strip():
                    session.run(statement)

def upsert_source_record(record: dict, department: str = "Agriculture – Farmers Welfare") -> dict:
    """Store an auditable source record; scheme extraction is deliberately separate."""
    source_url = record["url"]
    source_id = _id(source_url)
    with driver() as d:
        with d.session(database=settings.neo4j_database) as session:
            session.run("""
                MERGE (src:Source {url: $url})
                SET src.id=$id, src.title=$title, src.text=$text,
                    src.status=$status, src.source_type=$source_type,
                    src.updated_at=datetime()
                MERGE (dep:Department {name: $department})
                MERGE (dep)-[:HAS_SOURCE]->(src)
            """, url=source_url, id=source_id, title=record["title"],
                 text=record["text"], status=record.get("status"),
                 source_type=record.get("source_type", "official_web_page"),
                 department=department)
    return {"source_id": source_id, "url": source_url}

def upsert_scheme(name: str, description: str, source_url: str, department: str,
                  beneficiaries: list[str] | None = None,
                  benefits: list[str] | None = None,
                  eligibility: list[str] | None = None) -> str:
    """Store a verified scheme and its explicit relationships."""
    scheme_id = _id(f"{name}|{source_url}")
    with driver() as d:
        with d.session(database=settings.neo4j_database) as session:
            session.run("""
                MERGE (dep:Department {name:$department})
                MERGE (src:Source {url:$url})
                MERGE (s:Scheme {id:$id})
                SET s.name=$name, s.description=$description, s.updated_at=datetime()
                MERGE (dep)-[:HAS_SCHEME]->(s)
                MERGE (s)-[:SUPPORTED_BY]->(src)
            """, department=department, url=source_url, id=scheme_id,
                 name=name, description=description)
            for label, relation, values in [
                ("Beneficiary", "MAY_BENEFIT", beneficiaries or []),
                ("Benefit", "OFFERS_BENEFIT", benefits or []),
                ("Eligibility", "HAS_ELIGIBILITY", eligibility or []),
            ]:
                for value in values:
                    session.run(f"""
                        MATCH (s:Scheme {{id:$id}})
                        MERGE (n:{label} {{name:$value}})
                        MERGE (s)-[:{relation}]->(n)
                    """, id=scheme_id, value=value)
    return scheme_id
