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
                "scientific_name": "Vulpes vulpes",
                "kingdom": "Animalia",
                "phylum": "Chordata",
                "taxon_class": "Mammalia",
                "family": "Canidae",
                "genus": "Vulpes",
                "species": "Vulpes vulpes",
                "observations": 50,
                "countries": "ES",
                "first_year": 2000,
                "last_year": 2024,
                "avg_latitude": 40.0,
                "avg_longitude": -3.0,
                "most_common_basis": "HUMAN_OBSERVATION",
                "most_common_season": "otoño",
                "profile_text": "Mamífero rojizo de bosque.",
                "search_document": "Vulpes vulpes Mammalia zorro bosque rojizo",
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


def test_semantic_search_finds_flamingo_for_pajaro_rosa() -> None:
    """
    Debe encontrar flamenco al buscar pajaro rosa.
    """
    result_df = semantic_search_encyclopedia(
        encyclopedia_df=build_test_encyclopedia(),
        query_text="pajaro rosa",
        top_n=5,
    )

    assert not result_df.empty
    assert result_df.iloc[0]["scientific_name"] == "Phoenicopterus roseus"
