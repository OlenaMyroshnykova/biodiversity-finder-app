"""Tests para búsqueda de jaguar y felinos."""

import pandas as pd

from src.search import detect_intents, semantic_search_encyclopedia


def build_encyclopedia() -> pd.DataFrame:
    """Crea una enciclopedia mínima con jaguar y ruido."""
    return pd.DataFrame(
        [
            {
                "scientific_name": "Panthera onca",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "taxon_order": "Carnivora",
                "family": "Felidae",
                "genus": "Panthera",
                "observations": 100,
                "source_queries": "jaguar_panthera_onca, big_cats_felidae",
                "search_document": "Panthera onca jaguar Felidae felino big cat ягуар onça giaguaro",
            },
            {
                "scientific_name": "Casuarina equisetifolia",
                "kingdom": "Plantae",
                "taxon_class": "Magnoliopsida",
                "taxon_order": "Fagales",
                "family": "Casuarinaceae",
                "genus": "Casuarina",
                "observations": 2,
                "source_queries": "flowering_plants",
                "search_document": "Casuarina equisetifolia Plantae plant flor",
            },
            {
                "scientific_name": "Ursus maritimus",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "taxon_order": "Carnivora",
                "family": "Ursidae",
                "genus": "Ursus",
                "observations": 100,
                "source_queries": "polar_bear",
                "search_document": "Ursus maritimus oso polar bear",
            },
        ]
    )


def test_detects_jaguar_intent_in_russian() -> None:
    """Debe detectar ягуар."""
    names = {intent.name for intent in detect_intents("ягуар")}

    assert "jaguar_felidae" in names


def test_jaguar_search_returns_felidae_not_plants() -> None:
    """jaguar debe devolver Panthera/Felidae y no plantas."""
    result_df = semantic_search_encyclopedia(
        build_encyclopedia(),
        "jaguar",
        top_n=10,
    )

    assert not result_df.empty
    assert result_df.iloc[0]["scientific_name"] == "Panthera onca"
    assert set(result_df["family"]) == {"Felidae"}


def test_russian_jaguar_search_returns_panthera_onca() -> None:
    """ягуар debe devolver Panthera onca."""
    result_df = semantic_search_encyclopedia(
        build_encyclopedia(),
        "ягуар",
        top_n=10,
    )

    assert not result_df.empty
    assert result_df.iloc[0]["scientific_name"] == "Panthera onca"


def test_unknown_specific_query_does_not_return_weak_plants() -> None:
    """Consulta específica sin match no debe devolver plantas débiles."""
    no_jaguar_df = build_encyclopedia()
    no_jaguar_df = no_jaguar_df[no_jaguar_df["scientific_name"] != "Panthera onca"]

    result_df = semantic_search_encyclopedia(
        no_jaguar_df,
        "ягуар",
        top_n=10,
    )

    assert result_df.empty
