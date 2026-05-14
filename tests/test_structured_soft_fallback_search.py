import pandas as pd

from src.natural_language_query import apply_natural_language_filters, parse_natural_language_query
from src.search import semantic_search_encyclopedia


def test_structured_words_are_removed_from_fallback_query() -> None:
    parsed = parse_natural_language_query("animal grande de la sabana")

    assert parsed.size_tags == ["large"]
    assert parsed.habitat_tags == ["savanna"]
    assert parsed.group_tags == ["animal"]
    assert parsed.remaining_text == ""


def test_failed_strict_filter_returns_soft_structured_candidates_not_random_names() -> None:
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Leptodactylus savagei",
                "vernacular_names": "Rana Grande de la Selva",
                "kingdom": "Animalia",
                "taxon_class": "Amphibia",
                "family": "Leptodactylidae",
                "size_tag": "large",
                "habitat_tag": "forest",
                "color_tag": "brown",
                "search_document": "Leptodactylus savagei Rana Grande de la Selva",
                "observations": 30,
            },
            {
                "scientific_name": "Panthera leo",
                "vernacular_names": "Lion | León",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "family": "Felidae",
                "size_tag": "large",
                "habitat_tag": "savanna",
                "color_tag": "brown",
                "search_document": "Panthera leo Lion León sabana savanna",
                "observations": 20,
            },
        ]
    )

    filtered, parsed, fallback_used = apply_natural_language_filters(df, "animal grande de la sabana")

    assert parsed.remaining_text == ""
    assert not fallback_used
    result = semantic_search_encyclopedia(filtered, "", top_n=2)
    assert result.iloc[0]["scientific_name"] == "Panthera leo"


def test_soft_fallback_prefers_structured_match_over_common_name_grande() -> None:
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Leptodactylus savagei",
                "vernacular_names": "Rana Grande de la Selva",
                "kingdom": "Animalia",
                "taxon_class": "Amphibia",
                "family": "Leptodactylidae",
                "size_tag": "medium",
                "habitat_tag": "forest",
                "color_tag": "brown",
                "search_document": "Leptodactylus savagei Rana Grande de la Selva",
                "observations": 500,
            },
            {
                "scientific_name": "Gazella dorcas",
                "vernacular_names": "Dorcas gazelle | gacela",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "family": "Bovidae",
                "size_tag": "large medium",
                "habitat_tag": "savanna desert grassland",
                "color_tag": "brown",
                "search_document": "Gazella dorcas Dorcas gazelle gacela",
                "observations": 10,
            },
        ]
    )

    filtered, parsed, fallback_used = apply_natural_language_filters(df, "animal grande de la sabana")
    filtered.attrs["structured_remaining_text"] = parsed.remaining_text
    result = semantic_search_encyclopedia(filtered, parsed.remaining_text, top_n=2)

    assert fallback_used is False or "structured_match_score" in filtered.columns
    assert result.iloc[0]["scientific_name"] == "Gazella dorcas"
