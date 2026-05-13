from __future__ import annotations

import pandas as pd

from src.utils.dataframe_filters import (
    apply_basic_filters,
    apply_taxon_class_filter,
    filter_project_scope,
    get_available_taxon_classes,
)


def test_dynamic_classes_exclude_fungi_and_unknown_scope() -> None:
    df = pd.DataFrame([
        {"kingdom": "Animalia", "taxon_class": "Mammalia", "observations": 10},
        {"kingdom": "Animalia", "taxon_class": "Aves", "observations": 20},
        {"kingdom": "Plantae", "taxon_class": "Magnoliopsida", "observations": 30},
        {"kingdom": "Fungi", "taxon_class": "Agaricomycetes", "observations": 40},
        {"kingdom": "", "taxon_class": "Arthoniomycetes", "observations": 50},
    ])

    assert get_available_taxon_classes(df) == ["Aves", "Magnoliopsida", "Mammalia"]


def test_apply_basic_filters_keeps_project_scope_and_selected_classes() -> None:
    df = pd.DataFrame([
        {"scientific_name": "Bird", "kingdom": "Animalia", "taxon_class": "Aves", "observations": 5},
        {"scientific_name": "Wolf", "kingdom": "Animalia", "taxon_class": "Mammalia", "observations": 50},
        {"scientific_name": "Mushroom", "kingdom": "Fungi", "taxon_class": "Agaricomycetes", "observations": 100},
    ])

    result = apply_basic_filters(df, selected_classes=["Mammalia", "Agaricomycetes"], min_observations=10)

    assert result["scientific_name"].tolist() == ["Wolf"]


def test_apply_taxon_class_filter_accepts_single_string() -> None:
    df = pd.DataFrame([
        {"taxon_class": "Aves"},
        {"taxon_class": "Mammalia"},
    ])

    result = apply_taxon_class_filter(df, "Aves")

    assert result["taxon_class"].tolist() == ["Aves"]
