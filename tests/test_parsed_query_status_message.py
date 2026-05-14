import pandas as pd

from src.natural_language_query import apply_natural_language_filters, parse_natural_language_query


def test_parsed_query_has_status_message_for_streamlit_ui() -> None:
    parsed = parse_natural_language_query("animal grande de la sabana")

    assert parsed.has_structured_filters
    assert "tamaño: large" in parsed.status_message
    assert "hábitat: savanna" in parsed.status_message
    assert "grupo: animal" in parsed.status_message


def test_structured_query_never_returns_whole_dataset_when_no_match() -> None:
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Forest species",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "habitat_tag": "forest mountain",
                "size_tag": "large",
                "tags_de_busqueda": "forest mountain large",
                "search_document": "forest mountain animalia mammalia",
            }
        ]
    )

    result, parsed, relaxed = apply_natural_language_filters(df, "animal grande de la sabana")

    assert parsed.has_structured_filters
    assert relaxed is True
    assert result.empty
