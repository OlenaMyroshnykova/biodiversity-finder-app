"""DataFrame filtering helpers for the Streamlit app.

This module is intentionally small and dependency-free because it is imported by
both the UI and the test suite. The app scope is Animalia + Plantae; Fungi and
other kingdoms are filtered out before sidebar class filters are applied.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

PROJECT_SCOPE_KINGDOMS: set[str] = {"Animalia", "Plantae"}
ALL_CLASS_OPTIONS: set[str] = {
    "Todas",
    "Todos",
    "All",
    "All classes",
    "Todas las clases",
    "Todos los grupos",
    "",
}


def _normalize_text(value: Any) -> str:
    """Return a stripped string without converting NaN-like values to useful text."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def _as_clean_list(value: object) -> list[str]:
    """Normalize a sidebar value to a clean list of strings.

    Streamlit widgets may return a single string, a tuple, a list, None, or an
    empty selection. Older versions of this helper checked membership before
    checking whether the value was a list, which raised ``TypeError`` for list
    values. Keep list handling first.
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
            cleaned = _normalize_text(item)
            if cleaned and cleaned not in ALL_CLASS_OPTIONS:
                result.append(cleaned)
        return result

    cleaned = _normalize_text(value)
    if cleaned in ALL_CLASS_OPTIONS:
        return []
    return [cleaned] if cleaned else []


def filter_project_scope(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the project scope: animals and plants.

    If the dataset does not contain a ``kingdom`` column, the function returns a
    copy unchanged. This keeps the helper safe for small unit-test fixtures.
    """
    if df is None or df.empty:
        return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()

    result = df.copy()
    if "kingdom" not in result.columns:
        return result

    kingdoms = result["kingdom"].fillna("").astype(str).str.strip()
    return result.loc[kingdoms.isin(PROJECT_SCOPE_KINGDOMS)].copy()


def get_available_taxon_classes(df: pd.DataFrame) -> list[str]:
    """Return taxonomic classes available in the current dataset scope."""
    if df is None or df.empty or "taxon_class" not in df.columns:
        return []

    scoped = filter_project_scope(df)
    if scoped.empty or "taxon_class" not in scoped.columns:
        return []

    classes = (
        scoped["taxon_class"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    classes = classes[classes != ""]
    return sorted(classes.unique().tolist())


def apply_taxon_class_filter(
    df: pd.DataFrame,
    selected_classes: object | None = None,
) -> pd.DataFrame:
    """Filter a dataframe by selected taxonomic classes."""
    if df is None or df.empty:
        return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()

    result = df.copy()
    selected = _as_clean_list(selected_classes)
    if not selected or "taxon_class" not in result.columns:
        return result

    taxon_class = result["taxon_class"].fillna("").astype(str).str.strip()
    return result.loc[taxon_class.isin(selected)].copy()


def apply_min_observations_filter(
    df: pd.DataFrame,
    min_observations: int | float | str | None = 0,
) -> pd.DataFrame:
    """Filter by the observations column when it exists."""
    if df is None or df.empty:
        return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()

    result = df.copy()
    if "observations" not in result.columns:
        return result

    try:
        minimum = float(min_observations or 0)
    except (TypeError, ValueError):
        minimum = 0.0

    observations = pd.to_numeric(result["observations"], errors="coerce").fillna(0)
    return result.loc[observations >= minimum].copy()


def apply_conservation_filter(
    df: pd.DataFrame,
    conservation_filter: str | None = None,
) -> pd.DataFrame:
    """Apply an optional conservation filter used by the sidebar."""
    if df is None or df.empty:
        return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()

    result = df.copy()
    option = _normalize_text(conservation_filter).lower()
    if not option or option in {"all", "todos", "todas", "all species"}:
        return result

    category_col = None
    for candidate in ("iucn_category", "conservation_status"):
        if candidate in result.columns:
            category_col = candidate
            break

    if option in {"threatened", "amenazadas", "amenazada", "en peligro"}:
        if "is_threatened" in result.columns:
            threatened = result["is_threatened"].fillna(False).astype(bool)
            return result.loc[threatened].copy()
        if category_col:
            categories = result[category_col].fillna("").astype(str).str.upper()
            return result.loc[categories.isin({"VU", "EN", "CR", "EW", "EX"})].copy()
        return result.iloc[0:0].copy()

    if option in {"official", "iucn", "iucn red list", "con datos iucn"}:
        if "conservation_source" in result.columns:
            source = result["conservation_source"].fillna("").astype(str).str.lower()
            return result.loc[source.eq("iucn red list")].copy()
        if "iucn_is_official" in result.columns:
            official = result["iucn_is_official"].fillna(False).astype(bool)
            return result.loc[official].copy()
        return result

    if option in {"no_data", "sin datos", "sin datos iucn", "no iucn data"}:
        if category_col:
            categories = result[category_col].fillna("").astype(str).str.upper()
            return result.loc[categories.isin({"", "NO_DATA", "NE", "NAN"})].copy()
        return result

    return result


def apply_basic_filters(
    df: pd.DataFrame,
    selected_classes: object | None = None,
    min_observations: int | float | str | None = 0,
    conservation_filter: str | None = None,
) -> pd.DataFrame:
    """Apply the app's basic sidebar filters in a stable order.

    Order matters:
    1. project scope, so Fungi cannot reappear even if selected by an old UI;
    2. minimum observations;
    3. selected taxonomic classes;
    4. optional conservation status.
    """
    if df is None:
        return pd.DataFrame()

    result = filter_project_scope(df)
    result = apply_min_observations_filter(result, min_observations)
    result = apply_taxon_class_filter(result, selected_classes)
    result = apply_conservation_filter(result, conservation_filter)
    return result.copy()


__all__ = [
    "PROJECT_SCOPE_KINGDOMS",
    "ALL_CLASS_OPTIONS",
    "filter_project_scope",
    "get_available_taxon_classes",
    "apply_taxon_class_filter",
    "apply_min_observations_filter",
    "apply_conservation_filter",
    "apply_basic_filters",
]
