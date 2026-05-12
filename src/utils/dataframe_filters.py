"""Filtros básicos de DataFrame para la app."""

from __future__ import annotations

import pandas as pd


def apply_basic_filters(
    df: pd.DataFrame,
    selected_classes: list[str],
    min_observations: int,
) -> pd.DataFrame:
    """Aplica filtros básicos con df[condición]."""
    filtered_df = df[df["observations"] >= min_observations].copy()

    if selected_classes:
        filtered_df = filtered_df[filtered_df["taxon_class"].isin(selected_classes)]

    return filtered_df
