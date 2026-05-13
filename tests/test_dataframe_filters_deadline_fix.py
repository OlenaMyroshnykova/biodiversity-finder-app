import pandas as pd

from src.utils.dataframe_filters import (
    apply_basic_filters,
    filter_project_scope,
    get_available_taxon_classes,
)


def test_available_classes_are_dynamic_and_exclude_fungi():
    df = pd.DataFrame(
        [
            {"kingdom": "Animalia", "taxon_class": "Mammalia", "observations": 10},
            {"kingdom": "Animalia", "taxon_class": "Aves", "observations": 20},
            {"kingdom": "Plantae", "taxon_class": "Magnoliopsida", "observations": 30},
            {"kingdom": "Fungi", "taxon_class": "Agaricomycetes", "observations": 40},
        ]
    )

    assert get_available_taxon_classes(df) == ["Aves", "Magnoliopsida", "Mammalia"]


def test_filter_project_scope_keeps_only_animals_and_plants():
    df = pd.DataFrame(
        [
            {"kingdom": "Animalia", "taxon_class": "Aves", "observations": 10},
            {"kingdom": "Fungi", "taxon_class": "Agaricomycetes", "observations": 10},
        ]
    )

    result = filter_project_scope(df)

    assert result["kingdom"].tolist() == ["Animalia"]


def test_apply_basic_filters_uses_min_observations_and_selected_classes():
    df = pd.DataFrame(
        [
            {"kingdom": "Animalia", "taxon_class": "Aves", "observations": 5},
            {"kingdom": "Animalia", "taxon_class": "Mammalia", "observations": 50},
            {"kingdom": "Plantae", "taxon_class": "Magnoliopsida", "observations": 100},
        ]
    )

    result = apply_basic_filters(df, selected_classes=["Mammalia"], min_observations=10)

    assert result["taxon_class"].tolist() == ["Mammalia"]
