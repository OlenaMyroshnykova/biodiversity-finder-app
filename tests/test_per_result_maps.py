"""Tests para mapas por resultado."""

import pandas as pd

from src.map_components.species_map import (
    build_map_key,
    filter_points_for_species,
    filter_points_for_species_list,
)


def test_filter_points_for_species_exact_and_canonical() -> None:
    """Debe encontrar puntos por nombre canónico aunque la tarjeta tenga autoría."""
    points_df = pd.DataFrame(
        [
            {
                "scientific_name": "Panthera leo (Linnaeus, 1758)",
                "canonical_scientific_name": "Panthera leo",
                "decimalLatitude": -1.0,
                "decimalLongitude": 36.0,
            }
        ]
    )

    filtered_df = filter_points_for_species(points_df, "Panthera leo (Linnaeus, 1758)")

    assert len(filtered_df) == 1


def test_filter_points_for_species_list() -> None:
    """Debe poder filtrar puntos de varios resultados."""
    points_df = pd.DataFrame(
        [
            {
                "scientific_name": "Panthera leo",
                "canonical_scientific_name": "Panthera leo",
                "decimalLatitude": -1.0,
                "decimalLongitude": 36.0,
            },
            {
                "scientific_name": "Rana temporaria",
                "canonical_scientific_name": "Rana temporaria",
                "decimalLatitude": 40.0,
                "decimalLongitude": -3.0,
            },
            {
                "scientific_name": "Papilio machaon",
                "canonical_scientific_name": "Papilio machaon",
                "decimalLatitude": 41.0,
                "decimalLongitude": -2.0,
            },
        ]
    )

    filtered_df = filter_points_for_species_list(
        points_df,
        ["Panthera leo", "Rana temporaria"],
    )

    assert len(filtered_df) == 2
    assert set(filtered_df["canonical_scientific_name"]) == {
        "Panthera leo",
        "Rana temporaria",
    }


def test_build_map_key_is_stable() -> None:
    """Debe construir una key apta para Streamlit."""
    key = build_map_key("Panthera leo (Linnaeus, 1758)")

    assert key.startswith("species_map_")
    assert " " not in key
