"""Tests for IUCN UI behavior and clean structured vibe-search."""

from __future__ import annotations

import pandas as pd

from src.natural_language_query import apply_natural_language_filters, parse_natural_language_query
from src.search_components.query_expansion import expand_query


def build_search_df() -> pd.DataFrame:
    """Create a small dataframe that exposes the search architecture."""

    return pd.DataFrame(
        [
            {
                "scientific_name": "Panthera leo",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "family": "Felidae",
                "size_tag": "large grande",
                "habitat_tag": "savanna grassland sabana",
                "color_tag": "brown golden marron",
                "tags_de_busqueda": "brown golden marron savanna grassland sabana large grande",
                "vernacular_names": "Lion | León",
            },
            {
                "scientific_name": "Felis chaus",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "family": "Felidae",
                "size_tag": "medium mediano",
                "habitat_tag": "wetland river humedal",
                "color_tag": "brown marron",
                "tags_de_busqueda": "brown marron wetland river humedal medium mediano",
                "vernacular_names": "Jungle cat | Gato de la jungla",
            },
            {
                "scientific_name": "Papilio machaon",
                "kingdom": "Animalia",
                "taxon_class": "Insecta",
                "family": "Papilionidae",
                "size_tag": "small pequeño",
                "habitat_tag": "meadow forest garden",
                "color_tag": "colorful multicolor",
                "tags_de_busqueda": "colorful multicolor meadow forest garden small pequeño",
                "vernacular_names": "Swallowtail butterfly",
            },
        ]
    )


def test_spanish_query_is_parsed_to_structured_intent() -> None:
    """A natural Spanish query must become explicit structured filters."""

    parsed = parse_natural_language_query("animal grande de la sabana")

    assert parsed.group_tags == ["animal"]
    assert parsed.size_tags == ["large"]
    assert parsed.habitat_tags == ["savanna"]


def test_structured_filters_return_only_matching_rows() -> None:
    """Structured search must filter by tags and taxonomy, not by name noise."""

    result_df, parsed, fallback = apply_natural_language_filters(
        build_search_df(),
        "animal grande de la sabana",
    )

    assert parsed.has_structured_filters
    assert fallback is False
    assert result_df["scientific_name"].tolist() == ["Panthera leo"]
    assert result_df["size_tag"].str.contains("large").all()
    assert result_df["habitat_tag"].str.contains("savanna").all()


def test_common_names_do_not_override_structured_filters() -> None:
    """Common names are display/fallback data, not the main vibe-search signal."""

    df = build_search_df()
    df.loc[df["scientific_name"] == "Felis chaus", "vernacular_names"] = "large savanna animal"

    result_df, _, fallback = apply_natural_language_filters(df, "animal grande de la sabana")

    assert fallback is False
    assert result_df["scientific_name"].tolist() == ["Panthera leo"]


def test_query_expansion_is_spanish_english_only_for_demo() -> None:
    """No Russian/Ukrainian demo promises in fallback expansion."""

    expanded = expand_query("lion cocodrilo")

    assert "panthera leo" in expanded
    assert "crocodylia" in expanded
    assert "крокодил" not in expanded
    assert "тварина" not in expanded
