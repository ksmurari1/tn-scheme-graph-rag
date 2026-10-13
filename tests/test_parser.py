from src.scheme_graph.parser import clean_text, page_to_record

def test_clean_text_normalizes_whitespace():
    assert clean_text("A\xa0 B\n\n\nC") == "A B\n\nC"

def test_page_to_record_keeps_provenance():
    record = page_to_record({
        "title": " Scheme Page ",
        "final_url": "https://example.gov/scheme",
        "status": 200,
        "text": "This is a sufficiently long official scheme page text " * 4,
    })
    assert record is not None
    assert record["url"] == "https://example.gov/scheme"
    assert record["source_type"] == "official_web_page"

def test_page_to_record_rejects_short_page():
    assert page_to_record({"title":"Empty", "final_url":"https://example.gov", "text":"tiny"}) is None
