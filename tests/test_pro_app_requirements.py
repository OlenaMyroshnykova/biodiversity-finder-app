"""Tests para nuevos requisitos de la app."""

import pandas as pd

from src.map_components.species_map import filter_points_for_species
from src.natural_language_query import (
    apply_natural_language_filters,
    parse_natural_language_query,
)
from src.search import semantic_search_encyclopedia
from src.sighting_narratives import build_sighting_narrative


def build_test_encyclopedia() -> pd.DataFrame:
    """Crea una enciclopedia mínima."""
    return pd.DataFrame(
        [
            {
                "scientific_name": "Allionia incarnata L.",
                "vernacular_names": "Allionia incarnata L.",
                "taxon_class": "Magnoliopsida",
                "family": "Nyctaginaceae",
                "genus": "Allionia",
                "observations": 2,
                "conservation_status": "LC",
                "conservation_category": "Least Concern",
                "is_threatened": False,
                "color_tag": "green colorful",
                "habitat_tag": "terrestrial meadow",
                "size_tag": "small medium",
                "tags_de_busqueda": "green colorful terrestrial meadow small medium plant",
                "profile_text": "Flowering plant.",
                "search_document": "Allionia incarnata flowering plant.",
            },
            {
                "scientific_name": "Panthera leo (Linnaeus, 1758)",
                "vernacular_names": "Lion | León | Лев",
                "taxon_class": "Mammalia",
                "family": "Felidae",
                "genus": "Panthera",
                "observations": 120,
                "conservation_status": "VU",
                "conservation_category": "Vulnerable",
                "is_threatened": True,
                "color_tag": "brown golden",
                "habitat_tag": "savanna forest",
                "size_tag": "large",
                "tags_de_busqueda": "brown golden savanna forest large lion león лев mammalia felidae",
                "profile_text": "Large cat.",
                "search_document": "Panthera leo big cat lion león лев.",
            },
            {
                "scientific_name": "Tenebrionidae desert beetle",
                "vernacular_names": "Desert beetle",
                "taxon_class": "Insecta",
                "family": "Tenebrionidae",
                "genus": "Unknown",
                "observations": 10,
                "conservation_status": "DD",
                "conservation_category": "Data Deficient",
                "is_threatened": False,
                "color_tag": "brown",
                "habitat_tag": "desert arid",
                "size_tag": "small",
                "tags_de_busqueda": "brown desert arid small insect bicho",
                "profile_text": "Small desert insect.",
                "search_document": "small desert insect beetle bicho.",
            },
        ]
    )


def test_parse_natural_language_query_detects_vibe_tags() -> None:
    """Debe detectar tamaño, hábitat y grupo."""
    parsed = parse_natural_language_query("un bicho pequeño que vive en el desierto")

    assert "small" in parsed.size_tags
    assert "desert" in parsed.habitat_tags
    assert "insect" in parsed.group_tags


def test_apply_natural_language_filters_uses_df_loc_logic() -> None:
    """Debe filtrar con máscaras booleanas."""
    df = build_test_encyclopedia()

    filtered_df, parsed = apply_natural_language_filters(
        df,
        "un bicho pequeño que vive en el desierto",
    )

    assert parsed.has_structured_filters
    assert len(filtered_df) == 1
    assert filtered_df.iloc[0]["scientific_name"] == "Tenebrionidae desert beetle"


def test_lion_common_name_ranks_before_allionia_substring() -> None:
    """Lion debe ganar a Allionia cuando existe como nombre común."""
    result_df = semantic_search_encyclopedia(
        build_test_encyclopedia(),
        "lion",
        top_n=5,
    )

    assert result_df.iloc[0]["scientific_name"] == "Panthera leo (Linnaeus, 1758)"


def test_sighting_narrative_uses_dataframe_values() -> None:
    """La ficha narrativa debe usar datos de la fila."""
    row = build_test_encyclopedia().iloc[1]

    narrative = build_sighting_narrative(row)

    assert "Panthera leo" in narrative
    assert "Mammalia" in narrative
    assert "Vulnerable" in narrative


def test_filter_points_for_species_supports_canonical_name() -> None:
    """Debe filtrar puntos por especie seleccionada."""
    points_df = pd.DataFrame(
        [
            {
                "scientific_name": "Panthera leo (Linnaeus, 1758)",
                "canonical_scientific_name": "Panthera leo",
                "decimalLatitude": -1.0,
                "decimalLongitude": 36.0,
            },
            {
                "scientific_name": "Allionia incarnata L.",
                "canonical_scientific_name": "Allionia incarnata",
                "decimalLatitude": 10.0,
                "decimalLongitude": 10.0,
            },
        ]
    )

    filtered_df = filter_points_for_species(points_df, "Panthera leo")

    assert len(filtered_df) == 1
    assert filtered_df.iloc[0]["canonical_scientific_name"] == "Panthera leo"
