import pandas as pd

from src.natural_language_query import apply_natural_language_filters, parse_natural_language_query


def test_structured_query_keeps_savanna_and_does_not_return_forest() -> None:
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Forest species",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "habitat_tag": "forest mountain",
                "size_tag": "large",
                "observations": 100,
            },
            {
                "scientific_name": "Savanna species",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "habitat_tag": "savanna grassland",
                "size_tag": "medium",
                "observations": 10,
            },
        ]
    )

    result, parsed, relaxed = apply_natural_language_filters(df, "animal grande de la sabana")

    assert parsed.has_structured_filters
    assert relaxed is True
    assert list(result["scientific_name"]) == ["Savanna species"]


def test_structured_query_returns_empty_instead_of_contradictory_results() -> None:
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Forest species",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "habitat_tag": "forest mountain",
                "size_tag": "large",
            }
        ]
    )

    result, parsed, relaxed = apply_natural_language_filters(df, "animal grande de la sabana")

    assert parsed.has_structured_filters
    assert relaxed is True
    assert result.empty


def test_remaining_text_removes_structured_words() -> None:
    parsed = parse_natural_language_query("animal grande de la sabana")
    assert "grande" not in parsed.remaining_text
    assert "sabana" not in parsed.remaining_text
    assert parsed.habitat_tags == ["savanna"]
    assert parsed.size_tags == ["large"]
