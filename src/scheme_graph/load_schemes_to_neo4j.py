
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATA_FILE = PROJECT_ROOT / "data" / "processed" / "schemes_normalized.json"

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "7907a231")


def main():
    if not URI or not PASSWORD:
        raise RuntimeError("NEO4J_URI or NEO4J_PASSWORD is missing in .env")

    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Normalized data not found: {DATA_FILE}")

    with DATA_FILE.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    schemes = payload["schemes"]

    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    try:
        driver.verify_connectivity()

        with driver.session(database=DATABASE) as session:
            session.run("""
                CREATE CONSTRAINT department_code_unique IF NOT EXISTS
                FOR (d:Department)
                REQUIRE d.code IS UNIQUE
            """).consume()

            session.run("""
                CREATE CONSTRAINT scheme_key_unique IF NOT EXISTS
                FOR (s:Scheme)
                REQUIRE s.scheme_key IS UNIQUE
            """).consume()

            query = """
            UNWIND $schemes AS item

            MERGE (d:Department {code: item.department_code})
            SET d.name = item.department_name,
                d.name_tamil = item.department_name_tamil

            MERGE (s:Scheme {
                scheme_key: item.department_code + ':' + item.scheme_id
            })
            SET s.scheme_id = item.scheme_id,
                s.name = item.scheme_name,
                s.name_tamil = item.scheme_name_tamil,
                s.year = item.year,
                s.active = item.active,
                s.delete_status = item.delete_status,
                s.description = item.description,
                s.description_tamil = item.description_tamil,
                s.eligibility = item.eligibility,
                s.eligibility_tamil = item.eligibility_tamil,
                s.required_documents = item.required_documents,
                s.required_documents_tamil = item.required_documents_tamil,
                s.input_ids = item.input_ids,
                s.guideline_document = item.guideline_document,
                s.priority_scheme = item.priority_scheme,
                s.main_scheme_id = item.main_scheme_id,
                s.source_url = item.source_url

            MERGE (d)-[:OFFERS]->(s)
            """

            result = session.run(query, schemes=schemes)
            summary = result.consume()

            print("SmartAgri AI - Neo4j Ingestion")
            print("-" * 40)
            print("Normalized records submitted:", len(schemes))
            print("Query completed successfully.")

            counts = session.run("""
                MATCH (d:Department)
                WITH count(d) AS departments
                MATCH (s:Scheme)
                WITH departments, count(s) AS schemes
                MATCH (:Department)-[r:OFFERS]->(:Scheme)
                RETURN departments, schemes, count(r) AS relationships
            """).single()

            print("Departments in graph:", counts["departments"])
            print("Schemes in graph:", counts["schemes"])
            print("OFFERS relationships:", counts["relationships"])

    finally:
        driver.close()


if __name__ == "__main__":
    main()
