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
    "flamenco": "phoenicopterus roseus ave rosa humedal laguna marisma",
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
    "rapaz": "aves aguila eagle aquila",
    "aguila": "aquila chrysaetos ave rapaz",
    "águila": "aquila chrysaetos ave rapaz",
    "montana": "montaña mountain aquila chrysaetos",
    "montaña": "montana mountain aquila chrysaetos",
}

BIRD_TERMS = {"pajaro", "pajaros", "ave", "aves", "bird", "flamenco", "rapaz", "aguila", "águila"}
PLANT_TERMS = {"planta", "flor", "vegetal", "arbol", "árbol"}


def normalize_text(text: str) -> str:
    """
    Normaliza texto: minúsculas, sin acentos y sin signos raros.
    """
    normalized = unicodedata.normalize("NFKD", str(text).lower())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9ñ\s]", " ", without_accents).strip()


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
    top_n: int = 20,
) -> pd.DataFrame:
    """
    Busca en la enciclopedia usando TF-IDF, similitud coseno y pequeños ajustes
    taxonómicos para búsquedas humanas como "pajaro rosa".
    """
    result_df = encyclopedia_df.copy()

    if result_df.empty:
        return result_df

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
    result_df = apply_taxonomic_boosts(result_df, query_text)

    result_df = result_df[result_df["search_score"] > 0.005]

    return (
        result_df
        .sort_values(["search_score", "observations"], ascending=[False, False])
        .head(top_n)
        .reset_index(drop=True)
    )


def apply_taxonomic_boosts(result_df: pd.DataFrame, query_text: str) -> pd.DataFrame:
    """
    Ajusta la puntuación cuando la búsqueda contiene pistas taxonómicas claras.

    Ejemplo:
    - "pajaro rosa" debe priorizar Aves.
    - "planta flor" debe priorizar Plantae/Magnoliopsida.
    """
    normalized_query = normalize_text(query_text)
    query_words = set(normalized_query.split())

    result_df = result_df.copy()

    if query_words & BIRD_TERMS:
        bird_mask = result_df["taxon_class"].fillna("").str.lower().eq("aves")
        plant_mask = result_df["kingdom"].fillna("").str.lower().eq("plantae")

        result_df.loc[bird_mask, "search_score"] += 0.08

        if not query_words & PLANT_TERMS:
            result_df.loc[plant_mask, "search_score"] *= 0.35

    if query_words & PLANT_TERMS:
        plant_mask = result_df["kingdom"].fillna("").str.lower().eq("plantae")
        result_df.loc[plant_mask, "search_score"] += 0.08

    return result_df


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
