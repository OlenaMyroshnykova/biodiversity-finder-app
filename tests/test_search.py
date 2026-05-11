"""Tests de búsqueda semántica."""

import pandas as pd

from src.search import expand_query, normalize_text, semantic_search_encyclopedia


def build_test_encyclopedia() -> pd.DataFrame:
    """
    Crea enciclopedia mínima para tests.
    """
    return pd.DataFrame(
        [
            {
                "scientific_name": "Phoenicopterus roseus",
                "kingdom": "Animalia",
                "phylum": "Chordata",
                "taxon_class": "Aves",
                "family": "Phoenicopteridae",
                "genus": "Phoenicopterus",
                "species": "Phoenicopterus roseus",
                "observations": 100,
                "countries": "ES",
                "first_year": 2000,
                "last_year": 2024,
                "avg_latitude": 38.0,
                "avg_longitude": -0.5,
                "most_common_basis": "HUMAN_OBSERVATION",
                "most_common_season": "primavera",
                "profile_text": "Ave flamenco de color rosa que vive en humedales.",
                "search_document": "Phoenicopterus roseus Aves flamenco rosa humedal pajaro ave",
            },
            {
                "scientific_name": "Rosa canina",
                "kingdom": "Plantae",
                "phylum": "Tracheophyta",
                "taxon_class": "Magnoliopsida",
                "family": "Rosaceae",
                "genus": "Rosa",
                "species": "Rosa canina",
                "observations": 50,
                "countries": "ES",
                "first_year": 2000,
                "last_year": 2024,
                "avg_latitude": 40.0,
                "avg_longitude": -3.0,
                "most_common_basis": "HUMAN_OBSERVATION",
                "most_common_season": "primavera",
                "profile_text": "Planta con flor rosa.",
                "search_document": "Rosa canina Plantae Magnoliopsida flor rosa planta",
            },
        ]
    )


def test_normalize_text_removes_accents() -> None:
    """
    Debe normalizar acentos.
    """
    assert normalize_text("pájaro rosa") == "pajaro rosa"


def test_expand_query_supports_pajaro_rosa() -> None:
    """
    Debe expandir pajaro rosa hacia aves y flamenco.
    """
    expanded = expand_query("pajaro rosa")

    assert "aves" in expanded
    assert "flamenco" in expanded
    assert "phoenicopterus" in expanded


def test_semantic_search_finds_flamingo_before_rose_for_pajaro_rosa() -> None:
    """
    Debe priorizar el flamenco frente a la planta Rosa canina.
    """
    result_df = semantic_search_encyclopedia(
        encyclopedia_df=build_test_encyclopedia(),
        query_text="pajaro rosa",
        top_n=5,
    )

    assert not result_df.empty
    assert result_df.iloc[0]["scientific_name"] == "Phoenicopterus roseus"
