"""Tests para búsqueda inteligente general."""

import pandas as pd

from src.search import detect_intents, expand_query, semantic_search_encyclopedia


def build_encyclopedia() -> pd.DataFrame:
    """Crea enciclopedia mínima para tests."""
    return pd.DataFrame(
        [
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


def test_expand_query_adds_synonyms() -> None:
    """Debe expandir términos humanos."""
    expanded = expand_query("bicho con alas")

    assert "insecto" in expanded or "insecta" in expanded


def test_detect_intents_for_butterfly() -> None:
    """Debe detectar intención de mariposa."""
    intents = detect_intents("insecto mariposa")
    names = {intent.name for intent in intents}

    assert "butterfly" in names
    assert "insect" in names


def test_search_finds_polar_bear() -> None:
    """Debe encontrar oso polar por descripción humana."""
    result_df = semantic_search_encyclopedia(
        encyclopedia_df=build_encyclopedia(),
        query_text="animal polar hielo",
        top_n=5,
    )

    assert result_df.iloc[0]["scientific_name"] == "Ursus maritimus"


def test_search_finds_butterfly() -> None:
    """Debe encontrar mariposa por lenguaje humano."""
    result_df = semantic_search_encyclopedia(
        encyclopedia_df=build_encyclopedia(),
        query_text="bicho con alas",
        top_n=5,
    )

    assert result_df.iloc[0]["scientific_name"] == "Vanessa atalanta"


def test_search_finds_frog() -> None:
    """Debe encontrar anfibio por rana verde rio."""
    result_df = semantic_search_encyclopedia(
        encyclopedia_df=build_encyclopedia(),
        query_text="rana verde rio",
        top_n=5,
    )

    assert result_df.iloc[0]["scientific_name"] == "Rana temporaria"
