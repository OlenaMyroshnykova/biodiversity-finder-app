"""Tests de precisión general para búsqueda inteligente."""

import pandas as pd

from src.search import detect_intents, semantic_search_encyclopedia


def build_encyclopedia() -> pd.DataFrame:
    """Crea enciclopedia mínima con ruido intencional."""
    rows = [
        {
            "scientific_name": "Ursus maritimus",
            "kingdom": "Animalia",
            "taxon_class": "Mammalia",
            "taxon_order": "Carnivora",
            "family": "Ursidae",
            "genus": "Ursus",
            "observations": 2790,
            "source_queries": "polar_bear",
            "search_document": "Ursus maritimus Mammalia Carnivora Ursidae oso polar polar bear",
        },
        {
            "scientific_name": "Ursus americanus",
            "kingdom": "Animalia",
            "taxon_class": "Mammalia",
            "taxon_order": "Carnivora",
            "family": "Ursidae",
            "genus": "Ursus",
            "observations": 3,
            "source_queries": "mammals",
            "search_document": "Ursus americanus Mammalia Carnivora Ursidae bear oso",
        },
        {
            "scientific_name": "Papio ursinus",
            "kingdom": "Animalia",
            "taxon_class": "Mammalia",
            "taxon_order": "Primates",
            "family": "Cercopithecidae",
            "genus": "Papio",
            "observations": 5,
            "source_queries": "mammals",
            "search_document": "Papio ursinus Animalia Mammalia Primates Cercopithecidae",
        },
        {
            "scientific_name": "Sus scrofa",
            "kingdom": "Animalia",
            "taxon_class": "Mammalia",
            "taxon_order": "Artiodactyla",
            "family": "Suidae",
            "genus": "Sus",
            "observations": 30,
            "source_queries": "mammals",
            "search_document": "Sus scrofa Animalia Mammalia Artiodactyla Suidae",
        },
        {
            "scientific_name": "Vanessa atalanta",
            "kingdom": "Animalia",
            "taxon_class": "Insecta",
            "taxon_order": "Lepidoptera",
            "family": "Nymphalidae",
            "genus": "Vanessa",
            "observations": 50,
            "source_queries": "butterflies_lepidoptera",
            "search_document": "Vanessa atalanta Insecta Lepidoptera mariposa butterfly bicho con alas",
        },
        {
            "scientific_name": "Apis mellifera",
            "kingdom": "Animalia",
            "taxon_class": "Insecta",
            "taxon_order": "Hymenoptera",
            "family": "Apidae",
            "genus": "Apis",
            "observations": 500,
            "source_queries": "general_global",
            "search_document": "Apis mellifera Insecta Hymenoptera bee insecto",
        },
        {
            "scientific_name": "Rana temporaria",
            "kingdom": "Animalia",
            "taxon_class": "Amphibia",
            "taxon_order": "Anura",
            "family": "Ranidae",
            "genus": "Rana",
            "observations": 30,
            "source_queries": "amphibians",
            "search_document": "Rana temporaria Amphibia rana anfibio frog agua rio",
        },
        {
            "scientific_name": "Salmo salar",
            "kingdom": "Animalia",
            "taxon_class": "Actinopterygii",
            "taxon_order": "Salmoniformes",
            "family": "Salmonidae",
            "genus": "Salmo",
            "observations": 10,
            "source_queries": "general_global",
            "search_document": "Salmo salar fish agua rio",
        },
        {
            "scientific_name": "Rosa canina",
            "kingdom": "Plantae",
            "taxon_class": "Magnoliopsida",
            "taxon_order": "Rosales",
            "family": "Rosaceae",
            "genus": "Rosa",
            "observations": 200,
            "source_queries": "flowering_plants",
            "search_document": "Rosa canina Plantae Magnoliopsida planta flor flower",
        },
    ]

    return pd.DataFrame(rows)


def test_bear_search_returns_only_bears() -> None:
    """ведмідь debe devolver osos, no mamíferos genéricos."""
    result_df = semantic_search_encyclopedia(build_encyclopedia(), "ведмідь", top_n=10)

    assert not result_df.empty
    assert set(result_df["family"]) == {"Ursidae"}
    assert "Papio ursinus" not in set(result_df["scientific_name"])
    assert "Sus scrofa" not in set(result_df["scientific_name"])


def test_butterfly_search_returns_lepidoptera_not_all_insects() -> None:
    """mariposa debe devolver Lepidoptera, no insectos genéricos."""
    result_df = semantic_search_encyclopedia(build_encyclopedia(), "mariposa", top_n=10)

    assert not result_df.empty
    assert set(result_df["taxon_order"]) == {"Lepidoptera"}
    assert "Apis mellifera" not in set(result_df["scientific_name"])


def test_frog_search_returns_amphibia_not_fish() -> None:
    """rana rio debe priorizar Amphibia y no peces por la palabra agua/rio."""
    result_df = semantic_search_encyclopedia(build_encyclopedia(), "rana rio", top_n=10)

    assert not result_df.empty
    assert set(result_df["taxon_class"]) == {"Amphibia"}
    assert "Salmo salar" not in set(result_df["scientific_name"])


def test_flower_search_returns_plants_not_animals() -> None:
    """flor debe devolver plantas."""
    result_df = semantic_search_encyclopedia(build_encyclopedia(), "flor", top_n=10)

    assert not result_df.empty
    assert set(result_df["kingdom"]) == {"Plantae"}


def test_specific_intent_removes_broad_intent() -> None:
    """mariposa no debe quedarse solo como insecto genérico."""
    names = {intent.name for intent in detect_intents("insecto mariposa")}

    assert "butterfly" in names
    assert "insect" not in names
