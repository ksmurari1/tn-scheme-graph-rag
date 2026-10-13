
import sys
from pathlib import Path

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.scheme_graph.graph_retriever import SchemeGraphService


def main():
    service = SchemeGraphService()

    print("Graph overview:")
    print(service.get_overview())

    question = "Which schemes support cotton farmers?"
    print(f"\nQuestion: {question}")

    results = service.retrieve(question, limit=5)

    if not results:
        print("No keyword matches found.")
        return

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print("Scheme:", result["matched"])
        print("Department:", result["department"])
        print("Year:", result["year"])
        print("Active flag:", result["active"])
        print("Score:", result["score"])
        print("Evidence:", result["evidence"])
        print("Source:", result["source_url"])


if __name__ == "__main__":
    main()
