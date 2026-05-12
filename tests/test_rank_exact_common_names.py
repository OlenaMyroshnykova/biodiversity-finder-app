"""Tests de ranking: nombres comunes exactos deben ganar a substrings."""

import pandas as pd

from src.search import semantic_search_encyclopedia
from src.search_components.filters import has_exact_token_or_phrase_match


def build_test_encyclopedia() -> pd.DataFrame:
    """Crea una enciclopedia mínima para tests."""
    return pd.DataFrame(
        [
            {
                "scientific_name": "Allionia incarnata L.",
                "vernacular_names": "Allionia incarnata L.",
                "kingdom": "Plantae",
                "phylum": "Tracheophyta",
                "taxon_class": "Magnoliopsida",
                "taxon_order": "Caryophyllales",
                "family": "Nyctaginaceae",
                "genus": "Allionia",
                "species": "Allionia incarnata",
                "countries": "Unknown country",
                "source_queries": "flowering_plants",
                "observations": 2,
                "profile_text": "Flowering plant.",
                "search_document": "Allionia incarnata flowering plant.",
            },
            {
                "scientific_name": "Panthera leo (Linnaeus, 1758)",
                "vernacular_names": "Lion | León | Лев | Leão | Leone",
                "kingdom": "Animalia",
                "phylum": "Chordata",
                "taxon_class": "Mammalia",
                "taxon_order": "Carnivora",
                "family": "Felidae",
                "genus": "Panthera",
                "species": "Panthera leo",
                "countries": "Kenya | Tanzania | South Africa",
                "source_queries": "big_cats_felidae",
                "observations": 120,
                "profile_text": "Large cat.",
                "search_document": "Panthera leo big cat lion león лев.",
            },
        ]
    )


def test_token_match_does_not_boost_substring_inside_word() -> None:
    """lion no debe contar como token exacto dentro de Allionia."""
    assert not has_exact_token_or_phrase_match("Allionia incarnata", "lion")
    assert has_exact_token_or_phrase_match("Lion | León | Лев", "lion")


def test_lion_exact_common_name_ranks_before_allionia_substring() -> None:
    """Lion debe poner Panthera leo antes que Allionia."""
    result_df = semantic_search_encyclopedia(
        build_test_encyclopedia(),
        "lion",
        top_n=5,
    )

    assert not result_df.empty
    assert result_df.iloc[0]["scientific_name"] == "Panthera leo (Linnaeus, 1758)"


def test_leon_with_accent_ranks_lion_species_first() -> None:
    """León debe funcionar aunque se normalicen acentos."""
    result_df = semantic_search_encyclopedia(
        build_test_encyclopedia(),
        "león",
        top_n=5,
    )

    assert not result_df.empty
    assert result_df.iloc[0]["scientific_name"] == "Panthera leo (Linnaeus, 1758)"


def test_cyrillic_lion_ranks_lion_species_first() -> None:
    """Лев debe encontrar Panthera leo si existe en vernacular_names."""
    result_df = semantic_search_encyclopedia(
        build_test_encyclopedia(),
        "лев",
        top_n=5,
    )

    assert not result_df.empty
    assert result_df.iloc[0]["scientific_name"] == "Panthera leo (Linnaeus, 1758)"


def test_substring_match_can_still_return_result_when_no_exact_match_exists() -> None:
    """El fuzzy matching no se elimina por completo."""
    df = build_test_encyclopedia()
    df = df[df["scientific_name"].eq("Allionia incarnata L.")].copy()

    result_df = semantic_search_encyclopedia(df, "lion", top_n=5)

    assert not result_df.empty
    assert result_df.iloc[0]["scientific_name"] == "Allionia incarnata L."
