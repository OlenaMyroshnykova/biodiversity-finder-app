import pandas as pd

from src.natural_language_query import apply_natural_language_filters, parse_natural_language_query


def test_structured_query_keeps_habitat_and_does_not_return_contradictory_rows():
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Forest species",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "habitat_tag": "forest mountain",
                "size_tag": "large",
                "tags_de_busqueda": "large forest mountain",
                "search_document": "Forest species animalia mammalia forest mountain",
            },
            {
                "scientific_name": "Savanna species",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "habitat_tag": "savanna",
                "size_tag": "medium",
                "tags_de_busqueda": "medium savanna",
                "search_document": "Savanna species animalia mammalia savanna",
            },
        ]
    )

    filtered, parsed, relaxed = apply_natural_language_filters(df, "animal grande de la sabana")

    assert parsed.habitat_tags == ["savanna"]
    assert relaxed is True
    assert filtered["scientific_name"].tolist() == ["Savanna species"]


def test_structured_query_does_not_reuse_detected_words_as_text_query():
    parsed = parse_natural_language_query("animal grande de la sabana")

    assert parsed.remaining_text == ""
