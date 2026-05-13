"""Basic DataFrame filters for the Streamlit app."""
from __future__ import annotations

import pandas as pd

PROJECT_KINGDOMS = {"Animalia", "Plantae"}


def filter_project_scope(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only animals and plants, as required by the project brief."""
    if df.empty or "kingdom" not in df.columns:
        return df.copy()
    normalized_kingdom = df["kingdom"].fillna("").astype(str).str.strip()
    return df.loc[normalized_kingdom.isin(PROJECT_KINGDOMS)].copy()


def get_available_taxon_classes(df: pd.DataFrame) -> list[str]:
    """Return classes actually available in the current artifact."""
    scoped_df = filter_project_scope(df)
    if scoped_df.empty or "taxon_class" not in scoped_df.columns:
        return []
    classes = scoped_df["taxon_class"].dropna().astype(str).str.strip()
    classes = classes[classes.ne("")]
    return sorted(classes.unique().tolist())


def apply_basic_filters(
    df: pd.DataFrame,
    selected_classes: list[str],
    min_observations: int,
) -> pd.DataFrame:
    """Apply simple dataframe filters using df.loc."""
    filtered_df = filter_project_scope(df)

    if "observations" in filtered_df.columns:
        observations = pd.to_numeric(filtered_df["observations"], errors="coerce").fillna(0)
        filtered_df = filtered_df.loc[observations >= min_observations].copy()

    if selected_classes and "taxon_class" in filtered_df.columns:
        filtered_df = filtered_df.loc[filtered_df["taxon_class"].isin(selected_classes)].copy()

    return filtered_df
