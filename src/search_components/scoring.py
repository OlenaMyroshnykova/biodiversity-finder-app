"""Cálculo de puntuaciones de búsqueda."""

from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_tfidf_scores(
    documents: pd.Series,
    query: str,
    analyzer: str,
    ngram_range: tuple[int, int],
) -> pd.Series:
    """Calcula similitud TF-IDF entre documentos y consulta."""
    vectorizer = TfidfVectorizer(
        analyzer=analyzer,
        ngram_range=ngram_range,
        strip_accents="unicode",
        min_df=1,
    )

    matrix = vectorizer.fit_transform(list(documents) + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

    return pd.Series(scores, index=documents.index)
