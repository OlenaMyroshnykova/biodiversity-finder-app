from __future__ import annotations

import pandas as pd

from src.utils.dataframe_filters import (
    apply_basic_filters,
    filter_project_scope,
    get_available_taxon_classes,
)


def build_mixed_scope_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "scientific_name": "Canis lupus",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "observations": 10,
            },
            {
                "scientific_name": "Corvus corone",
                "kingdom": "Animalia",
                "taxon_class": "Aves",
                "observations": 3,
            },
            {
                "scientific_name": "Quercus ilex",
                "kingdom": "Plantae",
                "taxon_class": "Magnoliopsida",
                "observations": 5,
            },
            {
                "scientific_name": "Agaricus bisporus",
                "kingdom": "Fungi",
                "taxon_class": "Agaricomycetes",
                "observations": 20,
            },
            {
                "scientific_name": "Unknown",
                "kingdom": "",
                "taxon_class": "Arthoniomycetes",
                "observations": 20,
            },
        ]
    )


def test_available_taxon_classes_are_generated_from_current_dataset_scope() -> None:
    df = build_mixed_scope_df()

    classes = get_available_taxon_classes(df)

    assert classes == ["Aves", "Magnoliopsida", "Mammalia"]
    assert "Agaricomycetes" not in classes
    assert "Arthoniomycetes" not in classes


def test_filter_project_scope_keeps_only_animals_and_plants() -> None:
    df = build_mixed_scope_df()

    scoped_df = filter_project_scope(df)

    assert set(scoped_df["kingdom"]) == {"Animalia", "Plantae"}
    assert "Fungi" not in set(scoped_df["kingdom"])


def test_basic_filters_apply_project_scope_before_class_filter() -> None:
    df = build_mixed_scope_df()

    result = apply_basic_filters(
        df=df,
        selected_classes=["Agaricomycetes", "Mammalia"],
        min_observations=1,
    )

    assert list(result["taxon_class"]) == ["Mammalia"]
    assert list(result["scientific_name"]) == ["Canis lupus"]
