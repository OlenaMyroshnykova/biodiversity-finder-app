"""Tests for app-side structured vibe search requirements."""

import pandas as pd

from src.natural_language_query import parse_natural_language_query


def test_spanish_vibe_query_is_parsed_to_structured_filters() -> None:
    parsed = parse_natural_language_query("un bicho pequeño que vive en el desierto")

    assert "small" in parsed.size_tags
    assert "desert" in parsed.habitat_tags


def test_tags_de_busqueda_example_is_clean_not_multilingual_noise() -> None:
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Example species",
                "tags_de_busqueda": "brown savanna large",
                "search_document": "Example species mammalia bovidae common name",
            }
        ]
    )

    tags = df.loc[0, "tags_de_busqueda"]
    assert "brown" in tags
    assert "savanna" in tags
    assert "large" in tags
    assert "mammalia" not in tags
    assert "bovidae" not in tags
