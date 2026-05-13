"""DataFrame filters for the Streamlit app.

The app must not keep its own hardcoded taxon-class list. The available classes
are derived from the current artifact after applying the project scope
Animalia + Plantae.
"""
from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

PROJECT_KINGDOMS = {"Animalia", "Plantae"}
ALL_CLASS_OPTIONS = {"", "Todas", "Todos", "All", "all", "None", None}


def _as_clean_list(value: object) -> list[str]:
    """Normalize a sidebar value to a clean list of strings."""
    if value in ALL_CLASS_OPTIONS:
        return []

    if isinstance(value, str):
        value = value.strip()
        if value in ALL_CLASS_OPTIONS:
            return []
        return [value] if value else []

    if isinstance(value, Iterable):
        result: list[str] = []
        for item in value:
            if item in ALL_CLASS_OPTIONS:
                continue
            clean_item = str(item).strip()
            if clean_item:
                result.append(clean_item)
        return result

    return []


def filter_project_scope(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only animals and plants, as required by the project brief.

    If the dataframe has no ``kingdom`` column, the function returns a copy of
    the original data so tests and small demo dataframes do not break.
    """
    if df.empty or "kingdom" not in df.columns:
        return df.copy()

    normalized_kingdom = df["kingdom"].fillna("").astype(str).str.strip()
    scoped_df = df.loc[normalized_kingdom.isin(PROJECT_KINGDOMS)].copy()
    return scoped_df


def get_available_taxon_classes(df: pd.DataFrame) -> list[str]:
    """Return taxon classes actually available in the current artifact."""
    scoped_df = filter_project_scope(df)
    if scoped_df.empty or "taxon_class" not in scoped_df.columns:
        return []

    classes = scoped_df["taxon_class"].dropna().astype(str).str.strip()
    classes = classes[classes.ne("")]
    return sorted(classes.unique().tolist())


def apply_taxon_class_filter(
    df: pd.DataFrame,
    selected_class: str | list[str] | tuple[str, ...] | set[str] | None,
) -> pd.DataFrame:
    """Filter by one or several taxon classes."""
    selected_classes = _as_clean_list(selected_class)
    if not selected_classes or "taxon_class" not in df.columns:
        return df.copy()
    class_values = df["taxon_class"].fillna("").astype(str).str.strip()
    return df.loc[class_values.isin(selected_classes)].copy()


def apply_basic_filters(
    df: pd.DataFrame,
    selected_classes: list[str] | tuple[str, ...] | set[str] | str | None = None,
    min_observations: int | float = 0,
    conservation_filter: str | None = None,
    threatened_only: bool | None = None,
    **_: object,
) -> pd.DataFrame:
    """Apply lightweight sidebar filters using df.loc.

    Parameters are intentionally permissive because older UI code and tests used
    slightly different names/shapes while the app was being refactored.
    """
    filtered_df = filter_project_scope(df)

    if not filtered_df.empty and "observations" in filtered_df.columns:
        minimum = pd.to_numeric(pd.Series([min_observations]), errors="coerce").iloc[0]
        if pd.isna(minimum):
            minimum = 0
        observations = pd.to_numeric(filtered_df["observations"], errors="coerce").fillna(0)
        filtered_df = filtered_df.loc[observations >= float(minimum)].copy()

    selected_classes_list = _as_clean_list(selected_classes)
    if selected_classes_list and "taxon_class" in filtered_df.columns:
        class_values = filtered_df["taxon_class"].fillna("").astype(str).str.strip()
        filtered_df = filtered_df.loc[class_values.isin(selected_classes_list)].copy()

    if threatened_only is True and "is_threatened" in filtered_df.columns:
        filtered_df = filtered_df.loc[filtered_df["is_threatened"].fillna(False).astype(bool)].copy()

    if conservation_filter and conservation_filter not in {"Todas", "Todos", "All"}:
        normalized_filter = str(conservation_filter).strip().lower()
        if normalized_filter in {"amenazadas", "threatened", "amenazada"} and "is_threatened" in filtered_df.columns:
            filtered_df = filtered_df.loc[filtered_df["is_threatened"].fillna(False).astype(bool)].copy()
        elif normalized_filter in {"iucn", "oficial iucn", "official iucn"} and "conservation_source" in filtered_df.columns:
            source = filtered_df["conservation_source"].fillna("").astype(str)
            filtered_df = filtered_df.loc[source.str.contains("IUCN", case=False, na=False)].copy()
        elif "iucn_category" in filtered_df.columns:
            category = filtered_df["iucn_category"].fillna("").astype(str).str.upper()
            filtered_df = filtered_df.loc[category.eq(str(conservation_filter).upper())].copy()

    return filtered_df
