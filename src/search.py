"""Búsqueda semántica para la enciclopedia."""

from __future__ import annotations

import re
import unicodedata

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SPANISH_SYNONYMS = {
    "pajaro": "ave aves bird",
    "pajaros": "ave aves birds",
    "ave": "aves bird pajaro",
    "aves": "ave bird pajaro",
    "bird": "aves ave pajaro",
    "rosa": "rosado pink flamenco phoenicopterus roseus",
    "rosado": "rosa pink flamenco phoenicopterus roseus",
    "pink": "rosa rosado flamenco phoenicopterus roseus",
    "flamenco": "phoenicopterus roseus ave rosa humedal",
    "humedal": "wetland laguna marisma ave flamenco",
    "laguna": "humedal wetland flamenco ave",
    "rana": "amphibia anfibio frog",
    "anfibio": "amphibia rana frog",
    "rio": "río agua dulce amphibian amphibia rana",
    "río": "rio agua dulce amphibian amphibia rana",
    "pez": "actinopterygii fish pescado",
    "pescado": "pez fish actinopterygii",
    "mamifero": "mammalia mammal",
    "mamífero": "mammalia mammal",
    "oso": "mammalia ursus bear",
    "polar": "artico arctic ursus maritimus hielo",
    "artico": "ártico polar hielo ursus maritimus",
    "ártico": "artico polar hielo ursus maritimus",
    "hielo": "polar artico ursus maritimus",
    "insecto": "insecta insect",
    "planta": "plantae magnoliopsida vegetal",
    "flor": "plantae magnoliopsida planta",
    "rapaz": "aves aguila eagle",
    "aguila": "aquila chrysaetos ave rapaz",
    "águila": "aquila chrysaetos ave rapaz",
    "montana": "montaña mountain aquila chrysaetos",
    "montaña": "montana mountain aquila chrysaetos",
}


def normalize_text(text: str) -> str:
    """
    Normaliza texto: minúsculas, sin acentos y sin signos raros.
    """
    normalized = unicodedata.normalize("NFKD", str(text).lower())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9ñ\s]", " ", without_accents)


def expand_query(query_text: str) -> str:
    """
    Expande la consulta con sinónimos útiles para biodiversidad.
    """
    normalized_query = normalize_text(query_text)
    words = normalized_query.split()
    expansions = [normalized_query]

    for word in words:
        if word in SPANISH_SYNONYMS:
            expansions.append(SPANISH_SYNONYMS[word])

    return " ".join(expansions)


def semantic_search_encyclopedia(
    encyclopedia_df: pd.DataFrame,
    query_text: str,
    top_n: int = 50,
) -> pd.DataFrame:
    """
    Busca en la enciclopedia usando TF-IDF y similitud coseno.

    Args:
        encyclopedia_df: Dataframe de especies agregadas.
        query_text: Texto escrito por el usuario.
        top_n: Número máximo de resultados.

    Returns:
        Dataframe ordenado por puntuación de búsqueda.
    """
    result_df = encyclopedia_df.copy()

    if "search_document" not in result_df.columns:
        result_df["search_document"] = result_df.apply(build_fallback_document, axis=1)

    if not query_text.strip():
        result_df["search_score"] = 0.0
        return result_df.sort_values("observations", ascending=False).head(top_n)

    documents = result_df["search_document"].fillna("").astype(str).apply(normalize_text)
    expanded_query = expand_query(query_text)

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        strip_accents="unicode",
    )

    matrix = vectorizer.fit_transform(list(documents) + [expanded_query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

    result_df["search_score"] = scores
    result_df = result_df[result_df["search_score"] > 0]

    return (
        result_df
        .sort_values(["search_score", "observations"], ascending=[False, False])
        .head(top_n)
        .reset_index(drop=True)
    )


def build_fallback_document(row: pd.Series) -> str:
    """
    Crea documento de búsqueda si falta la columna search_document.
    """
    columns = [
        "scientific_name",
        "kingdom",
        "phylum",
        "taxon_class",
        "family",
        "genus",
        "species",
        "profile_text",
    ]

    return " ".join(str(row.get(column, "")) for column in columns)
