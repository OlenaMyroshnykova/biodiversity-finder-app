"""Filtros y boosts genéricos para resultados de búsqueda."""

from __future__ import annotations

import re

import pandas as pd

from src.search_components.normalizer import normalize_text


HIGH_PRIORITY_COLUMNS = [
    "vernacular_names",
    "tags_de_busqueda",
]

MEDIUM_HIGH_PRIORITY_COLUMNS = [
    "scientific_name",
    "species",
    "genus",
]

MEDIUM_PRIORITY_COLUMNS = [
    "family",
    "taxon_order",
    "taxon_class",
    "kingdom",
    "habitat_tag",
    "size_tag",
    "color_tag",
]

LOW_PRIORITY_COLUMNS = [
    "profile_text",
    "search_document",
]


def apply_score_thresholds(
    result_df: pd.DataFrame,
    *,
    minimum_score: float = 0.015,
    relative_ratio: float = 0.08,
) -> pd.DataFrame:
    """Quita coincidencias residuales extremadamente bajas."""
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
    """Añade boosts por coincidencias exactas de token o frase."""
    if result_df.empty or not query_text.strip():
        return result_df

    boosted_df = result_df.copy()
    normalized_query = normalize_text(query_text)

    if not normalized_query:
        return boosted_df

    boost_groups = [
        (HIGH_PRIORITY_COLUMNS, 2.00),
        (MEDIUM_HIGH_PRIORITY_COLUMNS, 1.25),
        (MEDIUM_PRIORITY_COLUMNS, 0.60),
        (LOW_PRIORITY_COLUMNS, 0.35),
    ]

    boosted_df["exact_match_score"] = 0.0

    for columns, boost_value in boost_groups:
        for column in columns:
            if column not in boosted_df.columns:
                continue

            exact_mask = boosted_df[column].apply(
                lambda value: has_exact_token_or_phrase_match(value, normalized_query)
            )

            boosted_df.loc[exact_mask, "exact_match_score"] += boost_value

    boosted_df["search_score"] = (
        boosted_df["search_score"].fillna(0)
        + boosted_df["exact_match_score"].fillna(0)
    )

    return boosted_df


def has_exact_token_or_phrase_match(value: object, normalized_query: str) -> bool:
    """Comprueba coincidencia exacta de palabra o frase normalizada."""
    normalized_value = normalize_text(value)

    if not normalized_value or not normalized_query:
        return False

    query_tokens = normalized_query.split()

    if not query_tokens:
        return False

    if len(query_tokens) == 1:
        value_tokens = set(normalized_value.split())

        return query_tokens[0] in value_tokens

    pattern = r"(^|\s)" + re.escape(normalized_query) + r"($|\s)"

    return re.search(pattern, normalized_value) is not None
