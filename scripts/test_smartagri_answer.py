
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.scheme_graph.graph_retriever import SchemeGraphService
from src.scheme_graph.llm_service import answer_question


def main():
    question = "Which schemes mention cotton, and what documents do they require?"

    service = SchemeGraphService()
    evidence = service.retrieve(question, limit=5)

    print("Question:", question)
    print("Retrieved evidence records:", len(evidence))

    answer, sources = answer_question(question, evidence)

    print("\nSMARTAGRI AI ANSWER")
    print("-" * 50)
    print(answer)

    print("\nSOURCES")
    print("-" * 50)

    for source in sources:
        print("-", source["title"])
        print("  Year:", source.get("year") or "Not specified")
        print("  URL:", source["url"])


if __name__ == "__main__":
    main()
