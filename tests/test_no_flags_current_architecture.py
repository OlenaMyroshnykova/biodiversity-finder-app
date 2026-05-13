from __future__ import annotations

import pandas as pd

from src.natural_language_query import apply_natural_language_filters, parse_natural_language_query
from src.search_components.engine import build_search_document_series
from src.ui_components.config import get_supported_languages_text


def test_supported_languages_are_es_en_without_flags() -> None:
    languages = get_supported_languages_text()
    assert "Español" in languages
    assert "English" in languages
    assert "Русский" not in languages
    assert "Українська" not in languages


def test_spanish_query_becomes_structured_filters() -> None:
    parsed = parse_natural_language_query("animal grande de la sabana")
    assert "animal" in parsed.group_tags
    assert "large" in parsed.size_tags
    assert "savanna" in parsed.habitat_tags


def test_structured_search_filters_by_columns_not_common_names() -> None:
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Species one",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "size_tag": "large grande",
                "habitat_tag": "savanna grassland sabana",
                "color_tag": "brown",
                "vernacular_names": "random name",
            },
            {
                "scientific_name": "Species two",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "size_tag": "small pequeno",
                "habitat_tag": "wetland humedal",
                "color_tag": "brown",
                "vernacular_names": "large savanna animal",
            },
        ]
    )

    result, parsed, fallback = apply_natural_language_filters(df, "animal grande de la sabana")

    assert parsed.has_structured_filters
    assert not fallback
    assert result["scientific_name"].tolist() == ["Species one"]


def test_text_search_document_does_not_include_tags_de_busqueda() -> None:
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Species two",
                "vernacular_names": "common name",
                "tags_de_busqueda": "large savanna brown",
                "search_document": "base document",
            }
        ]
    )

    document = build_search_document_series(df).iloc[0]

    assert "common name" in document
    assert "large savanna brown" not in document
