"""Generic search engine for the visual encyclopedia."""
from __future__ import annotations

import pandas as pd

from src.search_components.filters import (
    apply_score_thresholds,
    boost_exact_text_matches,
)
from src.search_components.normalizer import normalize_text
from src.search_components.query_expansion import expand_query
from src.search_components.scoring import compute_tfidf_scores

# Fallback search document: names, taxonomy and human-readable text only.
# Structured vibe tags (size/habitat/color/tags_de_busqueda) are deliberately
# excluded because they are handled by natural_language_query.py via df.loc.
SEARCH_DOCUMENT_COLUMNS = [
    "scientific_name",
    "canonical_scientific_name",
    "vernacular_names",
    "common_name_es",
    "common_name_en",
    "kingdom",
    "phylum",
    "taxon_class",
    "taxon_order",
    "family",
    "genus",
    "species",
    "countries",
    "profile_text",
    "conservation_status",
    "conservation_category",
    "iucn_category",
    "iucn_status_label",
]


def build_search_document_series(df: pd.DataFrame) -> pd.Series:
    """Build text used for fallback semantic/name search.

    ``tags_de_busqueda`` is intentionally not included. That column belongs to
    the structured vibe-search layer, not to TF-IDF ranking.
    """
    if df.empty:
        return pd.Series([], index=df.index, dtype=str)

    if "search_document" in df.columns:
        base_document = df["search_document"].fillna("").astype(str)
    else:
        base_document = pd.Series([""] * len(df), index=df.index, dtype=str)

    for column in SEARCH_DOCUMENT_COLUMNS:
        if column not in df.columns:
            continue
        base_document = base_document + " " + df[column].fillna("").astype(str)

    return base_document


def semantic_search_encyclopedia(
    encyclopedia_df: pd.DataFrame,
    query_text: str,
    top_n: int = 20,
) -> pd.DataFrame:
    """Run fallback TF-IDF search over the encyclopedia."""
    result_df = encyclopedia_df.copy()
    if result_df.empty:
        return result_df

    result_df["search_document"] = build_search_document_series(result_df)

    if not query_text.strip():
        result_df["search_score"] = 0.0
        sort_columns = ["observations"] if "observations" in result_df.columns else None
        if sort_columns:
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
    result_df["search_score"] = (word_scores * 0.85) + (char_scores * 0.15)
    result_df = boost_exact_text_matches(result_df, query_text)
    result_df = apply_score_thresholds(result_df)

    sort_by = ["search_score"]
    ascending = [False]
    if "observations" in result_df.columns:
        sort_by.append("observations")
        ascending.append(False)

    return result_df.sort_values(sort_by, ascending=ascending).head(top_n).reset_index(drop=True)
