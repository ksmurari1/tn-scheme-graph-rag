from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    neo4j_uri: str = os.getenv("NEO4J_URI", "").strip()
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j").strip()
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "").strip()
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j").strip()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    max_pages: int = int(os.getenv("MAX_PAGES", "10"))
    source_urls: tuple[str, ...] = tuple(
        url.strip() for url in os.getenv(
            "SOURCE_URLS",
            "https://www.tn.gov.in/scheme_list.php?dep_id=Mg%3D%3D"
        ).split(",") if url.strip()
    )

settings = Settings()
