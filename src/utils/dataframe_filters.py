"""Helpers for filtering the biodiversity dataframe in the Streamlit app.

This module intentionally keeps the project scope simple for the final demo:
Animalia + Plantae only. The sidebar class list is derived from the current
artifact, not from a hardcoded list of old classes.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

PROJECT_SCOPE_KINGDOMS = {"Animalia", "Plantae"}
ALL_CLASS_OPTIONS = {"All", "Todos", "Todas", "All classes", "Todas las clases", ""}


def _as_clean_list(value: object) -> list[str]:
    """Normalize a sidebar value to a clean list of strings.

    Streamlit widgets may return a string, list, tuple, set, None, or values such
    as "All". The previous version checked membership before handling lists,
    which crashed with: TypeError: unhashable type: 'list'.
    """
    if value is None:
        return []

    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned in ALL_CLASS_OPTIONS:
            return []
        return [cleaned] if cleaned else []

    if isinstance(value, Iterable):
        result: list[str] = []
        for item in value:
            if item is None:
                continue
            cleaned = str(item).strip()
            if cleaned and cleaned not in ALL_CLASS_OPTIONS:
                result.append(cleaned)
        return result

    cleaned = str(value).strip()
    if cleaned in ALL_CLASS_OPTIONS:
        return []
    return [cleaned] if cleaned else []


def normalize_project_scope(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only Animalia and Plantae rows for the educational project scope."""
    if df is None or df.empty:
        return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()

    filtered_df = df.copy()
    if "kingdom" not in filtered_df.columns:
        return filtered_df

    kingdom_values = filtered_df["kingdom"].fillna("").astype(str).str.strip()
    return filtered_df.loc[kingdom_values.isin(PROJECT_SCOPE_KINGDOMS)].copy()


def get_available_taxon_classes(df: pd.DataFrame) -> list[str]:
    """Return sorted taxon classes available in the current artifact.

    The app must not show stale/hardcoded classes. Fungi are excluded because the
    project scope is animals and plants.
    """
    if df is None or df.empty or "taxon_class" not in df.columns:
        return []

    scoped_df = normalize_project_scope(df)
    if scoped_df.empty:
        return []

    classes = (
        scoped_df["taxon_class"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    classes = classes[classes.ne("")]
    return sorted(classes.drop_duplicates().tolist())


def apply_basic_filters(
    df: pd.DataFrame,
    selected_classes: object | None = None,
    min_observations: int | float | None = 0,
    **kwargs: Any,
) -> pd.DataFrame:
    """Apply basic dataframe filters used by the sidebar.

    The order is important:
    1. enforce project scope Animalia + Plantae;
    2. apply minimum observations;
    3. apply selected taxon classes from the *scoped* dataset.

    Extra keyword aliases are accepted for compatibility with older app/tests.
    """
    if df is None or df.empty:
        return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()

    if selected_classes is None:
        selected_classes = kwargs.get("taxon_classes", kwargs.get("selected_taxon_classes"))

    if min_observations is None:
        min_observations = kwargs.get("minimum_observations", kwargs.get("min_obs", 0))

    filtered_df = normalize_project_scope(df)

    try:
        minimum = float(min_observations or 0)
    except (TypeError, ValueError):
        minimum = 0.0

    if "observations" in filtered_df.columns and minimum > 0:
        observations = pd.to_numeric(filtered_df["observations"], errors="coerce").fillna(0)
        filtered_df = filtered_df.loc[observations >= minimum].copy()

    selected_classes_list = _as_clean_list(selected_classes)
    if selected_classes_list and "taxon_class" in filtered_df.columns:
        class_values = filtered_df["taxon_class"].fillna("").astype(str).str.strip()
        filtered_df = filtered_df.loc[class_values.isin(selected_classes_list)].copy()

    return filtered_df
