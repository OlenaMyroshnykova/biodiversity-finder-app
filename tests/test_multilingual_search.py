"""Tests para búsqueda multilingüe."""

import pandas as pd

from src.search import expand_query, semantic_search_encyclopedia


def build_encyclopedia() -> pd.DataFrame:
    """Crea una enciclopedia mínima para tests."""
    return pd.DataFrame(
        [
            {
                "scientific_name": "Ursus maritimus",
                "kingdom": "Animalia",
                "phylum": "Chordata",
                "taxon_class": "Mammalia",
                "taxon_order": "Carnivora",
                "family": "Ursidae",
                "genus": "Ursus",
                "species": "Ursus maritimus",
                "observations": 20,
                "countries": "CA",
                "first_year": 2020,
                "last_year": 2024,
                "avg_latitude": 70.0,
                "avg_longitude": -40.0,
                "most_common_basis": "HUMAN_OBSERVATION",
                "most_common_season": "invierno",
                "source_queries": "polar_bear",
                "profile_text": "Oso polar.",
                "search_document": "Ursus maritimus oso polar polar bear animal polar hielo ice",
            },
            {
                "scientific_name": "Vanessa atalanta",
                "kingdom": "Animalia",
                "phylum": "Arthropoda",
                "taxon_class": "Insecta",
                "taxon_order": "Lepidoptera",
                "family": "Nymphalidae",
                "genus": "Vanessa",
                "species": "Vanessa atalanta",
                "observations": 50,
                "countries": "ES",
                "first_year": 2020,
                "last_year": 2024,
                "avg_latitude": 40.0,
                "avg_longitude": -3.0,
                "most_common_basis": "HUMAN_OBSERVATION",
                "most_common_season": "primavera",
                "source_queries": "butterflies_lepidoptera",
                "profile_text": "Insecto del orden Lepidoptera.",
                "search_document": "Vanessa atalanta Insecta Lepidoptera mariposa butterfly bicho con alas",
            },
            {
                "scientific_name": "Phoenicopterus roseus",
                "kingdom": "Animalia",
                "phylum": "Chordata",
                "taxon_class": "Aves",
                "taxon_order": "Phoenicopteriformes",
                "family": "Phoenicopteridae",
                "genus": "Phoenicopterus",
                "species": "Phoenicopterus roseus",
                "observations": 20,
                "countries": "ES",
                "first_year": 2020,
                "last_year": 2024,
                "avg_latitude": 38.0,
                "avg_longitude": -0.5,
                "most_common_basis": "HUMAN_OBSERVATION",
                "most_common_season": "primavera",
                "source_queries": "flamingo_pink_bird",
                "profile_text": "Ave rosa de humedales.",
                "search_document": "Phoenicopterus roseus flamenco pajaro rosa ave rosa pink bird",
            },
            {
                "scientific_name": "Rana temporaria",
                "kingdom": "Animalia",
                "phylum": "Chordata",
                "taxon_class": "Amphibia",
                "taxon_order": "Anura",
                "family": "Ranidae",
                "genus": "Rana",
                "species": "Rana temporaria",
                "observations": 30,
                "countries": "ES",
                "first_year": 2020,
                "last_year": 2024,
                "avg_latitude": 42.0,
                "avg_longitude": -4.0,
                "most_common_basis": "HUMAN_OBSERVATION",
                "most_common_season": "primavera",
                "source_queries": "amphibians",
                "profile_text": "Anfibio asociado al agua.",
                "search_document": "Rana temporaria Amphibia rana anfibio frog agua rio",
            },
        ]
    )


def test_expand_query_ukrainian_butterfly() -> None:
    """Debe expandir metelik."""
    expanded = expand_query("метелик")

    assert "lepidoptera" in expanded
    assert "mariposa" in expanded


def test_search_ukrainian_polar_bear() -> None:
    """Debe encontrar oso polar en ucraniano."""
    result_df = semantic_search_encyclopedia(
        encyclopedia_df=build_encyclopedia(),
        query_text="білий ведмідь",
        top_n=5,
    )

    assert result_df.iloc[0]["scientific_name"] == "Ursus maritimus"


def test_search_portuguese_butterfly() -> None:
    """Debe encontrar mariposa en portugués."""
    result_df = semantic_search_encyclopedia(
        encyclopedia_df=build_encyclopedia(),
        query_text="borboleta",
        top_n=5,
    )

    assert result_df.iloc[0]["scientific_name"] == "Vanessa atalanta"


def test_search_italian_butterfly() -> None:
    """Debe encontrar mariposa en italiano."""
    result_df = semantic_search_encyclopedia(
        encyclopedia_df=build_encyclopedia(),
        query_text="farfalla",
        top_n=5,
    )

    assert result_df.iloc[0]["scientific_name"] == "Vanessa atalanta"


def test_search_russian_pink_bird() -> None:
    """Debe encontrar pájaro rosa en ruso."""
    result_df = semantic_search_encyclopedia(
        encyclopedia_df=build_encyclopedia(),
        query_text="розовая птица",
        top_n=5,
    )

    assert result_df.iloc[0]["scientific_name"] == "Phoenicopterus roseus"
