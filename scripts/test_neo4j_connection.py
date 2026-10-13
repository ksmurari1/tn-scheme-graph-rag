
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load .env from the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


def main():
    if not URI or not PASSWORD:
        print("ERROR: NEO4J_URI or NEO4J_PASSWORD is missing in .env")
        return

    driver = None

    try:
        driver = GraphDatabase.driver(
            URI,
            auth=(USERNAME, PASSWORD),
        )

        driver.verify_connectivity()
        print("SUCCESS: Connected to Neo4j AuraDB.")

        with driver.session(database=DATABASE) as session:
            result = session.run(
                "RETURN 1 AS connection_test, "
                "datetime() AS server_time"
            )
            record = result.single()

            print("Connection test:", record["connection_test"])
            print("Server time:", record["server_time"])
            print("Database:", DATABASE)

    except Exception as exc:
        print("CONNECTION FAILED:", type(exc).__name__)
        print("Check the URI, credentials, database status, and network access.")
        print("Detailed error:", str(exc))

    finally:
        if driver is not None:
            driver.close()


if __name__ == "__main__":
    main()
