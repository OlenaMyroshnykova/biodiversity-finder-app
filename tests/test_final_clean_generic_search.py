"""Tests para buscador final genérico."""

import pandas as pd

from src.search import semantic_search_encyclopedia
from src.search_components.engine import build_search_document_series
from src.search_components.query_expansion import GENERIC_CATEGORY_SYNONYMS, expand_query
from src.ui_components.species_cards import format_common_names
from src.utils.dataframe_filters import apply_basic_filters
from src.utils.formatting import format_coordinate


def build_test_encyclopedia() -> pd.DataFrame:
    """Crea una enciclopedia mínima con nombres comunes."""
    return pd.DataFrame(
        [
            {
                "scientific_name": "Panthera pardus",
                "vernacular_names": "Leopard | Leopardo | Леопард",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "taxon_order": "Carnivora",
                "family": "Felidae",
                "genus": "Panthera",
                "observations": 100,
                "profile_text": "Large spotted cat.",
            },
            {
                "scientific_name": "Rosa canina",
                "vernacular_names": "Dog rose | Rosa silvestre",
                "kingdom": "Plantae",
                "taxon_class": "Magnoliopsida",
                "taxon_order": "Rosales",
                "family": "Rosaceae",
                "genus": "Rosa",
                "observations": 200,
                "profile_text": "Flowering plant.",
            },
            {
                "scientific_name": "Strix aluco",
                "vernacular_names": "Tawny owl | Cárabo común | Серая неясыть",
                "kingdom": "Animalia",
                "taxon_class": "Aves",
                "taxon_order": "Strigiformes",
                "family": "Strigidae",
                "genus": "Strix",
                "observations": 150,
                "profile_text": "Nocturnal bird.",
            },
        ]
    )


def test_search_document_includes_vernacular_names_and_taxonomy() -> None:
    """El documento debe incluir nombres comunes y taxonomía."""
    documents = build_search_document_series(build_test_encyclopedia())

    assert "Leopardo" in documents.iloc[0]
    assert "Felidae" in documents.iloc[0]
    assert "Rosa silvestre" in documents.iloc[1]
    assert "Strigidae" in documents.iloc[2]


def test_search_finds_species_by_common_name_without_specific_hack() -> None:
    """Debe encontrar leopardo desde vernacular_names."""
    result_df = semantic_search_encyclopedia(
        build_test_encyclopedia(),
        "леопард",
        top_n=10,
    )

    assert not result_df.empty
    assert result_df.iloc[0]["scientific_name"] == "Panthera pardus"


def test_search_finds_plant_by_common_name() -> None:
    """Debe encontrar plantas por nombre común."""
    result_df = semantic_search_encyclopedia(
        build_test_encyclopedia(),
        "rosa silvestre",
        top_n=10,
    )

    assert not result_df.empty
    assert result_df.iloc[0]["scientific_name"] == "Rosa canina"


def test_search_finds_bird_by_common_name() -> None:
    """Debe encontrar aves por nombre común."""
    result_df = semantic_search_encyclopedia(
        build_test_encyclopedia(),
        "cárabo común",
        top_n=10,
    )

    assert not result_df.empty
    assert result_df.iloc[0]["scientific_name"] == "Strix aluco"


def test_generic_synonyms_do_not_contain_specific_animals() -> None:
    """El diccionario genérico no debe contener especies concretas."""
    forbidden_terms = {
        "jaguar",
        "leopard",
        "leopardo",
        "леопард",
        "tiger",
        "lion",
        "oso",
        "mariposa",
    }

    assert forbidden_terms.isdisjoint(set(GENERIC_CATEGORY_SYNONYMS))


def test_expand_query_keeps_generic_category_support() -> None:
    """La expansión conserva categorías amplias."""
    expanded_query = expand_query("animal")

    assert "animalia" in expanded_query


def test_format_common_names_removes_duplicates() -> None:
    """Debe formatear nombres comunes."""
    result = format_common_names("Leopard | Leopardo | Leopard | Леопард")

    assert result == "Leopard / Leopardo / Леопард"


def test_apply_basic_filters_uses_dataframe_conditions() -> None:
    """Debe mantener df[condición] para filtros básicos."""
    df = build_test_encyclopedia()

    filtered_df = apply_basic_filters(
        df=df,
        selected_classes=["Aves"],
        min_observations=100,
    )

    assert len(filtered_df) == 1
    assert filtered_df.iloc[0]["scientific_name"] == "Strix aluco"


def test_safe_coordinate_formatting() -> None:
    """Debe mantener formateo seguro."""
    assert format_coordinate(None) == "N/A"
    assert format_coordinate(38.12345) == "38.123"
