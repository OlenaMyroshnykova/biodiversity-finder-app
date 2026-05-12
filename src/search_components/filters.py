"""Filtros genéricos contra resultados débiles."""

from __future__ import annotations

import pandas as pd


def apply_score_thresholds(
    result_df: pd.DataFrame,
    *,
    minimum_score: float = 0.035,
    relative_ratio: float = 0.18,
) -> pd.DataFrame:
    """Quita resultados con coincidencia residual demasiado baja."""
    if result_df.empty or "search_score" not in result_df.columns:
        return result_df

    max_score = float(result_df["search_score"].max())

    if max_score <= 0:
        return result_df.iloc[0:0].copy()

    threshold = max(minimum_score, max_score * relative_ratio)

    return result_df[result_df["search_score"] >= threshold].copy()


def boost_exact_text_matches(
    result_df: pd.DataFrame,
    query_text: str,
) -> pd.DataFrame:
    """Da un pequeño boost a coincidencias exactas en nombres y taxonomía."""
    if result_df.empty or not query_text.strip():
        return result_df

    boosted_df = result_df.copy()
    normalized_query = query_text.strip().lower()

    exact_columns = [
        "scientific_name",
        "vernacular_names",
        "genus",
        "family",
        "taxon_order",
        "taxon_class",
        "kingdom",
    ]

    for column in exact_columns:
        if column not in boosted_df.columns:
            continue

        column_text = boosted_df[column].fillna("").astype(str).str.lower()
        exact_mask = column_text.str.contains(normalized_query, case=False, regex=False)

        boosted_df.loc[exact_mask, "search_score"] += 0.12

    return boosted_df
