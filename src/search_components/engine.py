"""Motor de búsqueda sobre el contrato de artifact.

La app no contiene reglas por especie. El ranking trabaja sobre `search_document`
y sobre las columnas contractuales que vienen del pipeline.
"""
from __future__ import annotations

import pandas as pd

from src.artifact_contract import SEARCH_CONTRACT_COLUMNS, build_runtime_search_document
from src.search_components.filters import apply_score_thresholds, boost_exact_text_matches
from src.search_components.normalizer import normalize_text
from src.search_components.query_expansion import expand_query
from src.search_components.scoring import compute_tfidf_scores


def build_search_document_series(df: pd.DataFrame) -> pd.Series:
    """Construye documento de búsqueda desde el contrato compartido."""
    if df.empty:
        return pd.Series([], index=df.index, dtype=str)
    return build_runtime_search_document(df)


def semantic_search_encyclopedia(
    encyclopedia_df: pd.DataFrame,
    query_text: str,
    top_n: int = 20,
) -> pd.DataFrame:
    """Busca por texto natural, nombres comunes, taxonomía y tags normalizados."""
    result_df = encyclopedia_df.copy()
    if result_df.empty:
        return result_df

    result_df["search_document"] = build_search_document_series(result_df)

    if not query_text.strip():
        result_df["search_score"] = 0.0
        if "observations" in result_df.columns:
            return result_df.sort_values("observations", ascending=False).head(top_n).reset_index(drop=True)
        return result_df.head(top_n).reset_index(drop=True)

    documents = result_df["search_document"].fillna("").astype(str).apply(normalize_text)
    expanded_query = expand_query(query_text)

    word_scores = compute_tfidf_scores(
        documents=documents,
        query=expanded_query,
        analyzer="word",
        ngram_range=(1, 2),
    )
    char_scores = compute_tfidf_scores(
        documents=documents,
        query=expanded_query,
        analyzer="char_wb",
        ngram_range=(3, 5),
    )

    result_df["word_score"] = word_scores
    result_df["char_score"] = char_scores
    result_df["search_score"] = (word_scores * 0.82) + (char_scores * 0.18)
    result_df = boost_exact_text_matches(result_df, query_text)
    result_df = apply_score_thresholds(result_df)

    sort_by = ["search_score"]
    ascending = [False]
    if "has_image" in result_df.columns:
        result_df["_has_image_sort"] = result_df["has_image"].fillna(False).astype(bool).astype(int)
        sort_by.append("_has_image_sort")
        ascending.append(False)
    if "observations" in result_df.columns:
        sort_by.append("observations")
        ascending.append(False)

    return result_df.sort_values(sort_by, ascending=ascending).head(top_n).reset_index(drop=True)
