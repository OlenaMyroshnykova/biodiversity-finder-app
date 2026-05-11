"""Búsqueda semántica inteligente para la enciclopedia."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class SearchIntent:
    """Representa una intención de búsqueda detectada."""

    name: str
    terms: set[str]
    boost_columns: dict[str, list[str]]
    boost_value: float


INTENT_DEFINITIONS = [
    SearchIntent(
        name="bird",
        terms={"pajaro", "pajaros", "ave", "aves", "bird", "birds", "alas", "plumas"},
        boost_columns={
            "taxon_class": ["aves"],
            "search_document": ["bird", "ave", "pajaro", "pájaro"],
        },
        boost_value=0.08,
    ),
    SearchIntent(
        name="pink_flamingo",
        terms={"flamenco", "rosa", "rosado", "pink"},
        boost_columns={
            "scientific_name": ["phoenicopterus roseus"],
            "search_document": ["flamenco", "flamingo", "pajaro rosa", "ave rosa"],
        },
        boost_value=0.14,
    ),
    SearchIntent(
        name="polar_bear",
        terms={"polar", "hielo", "ice", "oso", "bear", "ursus", "artico", "arctic", "nieve"},
        boost_columns={
            "scientific_name": ["ursus maritimus"],
            "source_queries": ["polar_bear"],
            "search_document": ["oso polar", "polar bear", "animal polar", "hielo"],
        },
        boost_value=0.20,
    ),
    SearchIntent(
        name="butterfly",
        terms={"mariposa", "mariposas", "butterfly", "butterflies", "polilla", "polillas", "moth", "moths", "lepidoptera"},
        boost_columns={
            "taxon_order": ["lepidoptera"],
            "source_queries": ["butterflies_lepidoptera"],
            "search_document": ["mariposa", "butterfly", "polilla", "lepidoptera"],
        },
        boost_value=0.20,
    ),
    SearchIntent(
        name="amphibian",
        terms={"rana", "ranas", "anfibio", "anfibios", "frog", "frogs", "rio", "río", "agua", "charca"},
        boost_columns={
            "taxon_class": ["amphibia"],
            "source_queries": ["amphibians"],
            "search_document": ["rana", "anfibio", "frog", "agua"],
        },
        boost_value=0.16,
    ),
    SearchIntent(
        name="raptor",
        terms={"rapaz", "rapaces", "aguila", "águila", "eagle", "hawk", "halcon", "halcón", "montaña"},
        boost_columns={
            "family": ["accipitridae"],
            "source_queries": ["raptors_accipitridae"],
            "search_document": ["ave rapaz", "eagle", "aguila", "águila", "montaña"],
        },
        boost_value=0.16,
    ),
    SearchIntent(
        name="plant",
        terms={"planta", "plantas", "flor", "flores", "vegetal", "flower", "flowers", "plant"},
        boost_columns={
            "kingdom": ["plantae"],
            "taxon_class": ["magnoliopsida", "liliopsida"],
            "source_queries": ["flowering_plants"],
            "search_document": ["planta", "flor", "flowering"],
        },
        boost_value=0.12,
    ),
    SearchIntent(
        name="mammal",
        terms={"mamifero", "mamífero", "mamiferos", "mamíferos", "mammal", "mammals"},
        boost_columns={
            "taxon_class": ["mammalia"],
            "source_queries": ["mammals"],
            "search_document": ["mamifero", "mamífero", "mammal"],
        },
        boost_value=0.08,
    ),
    SearchIntent(
        name="insect",
        terms={"insecto", "insectos", "insect", "insects", "bicho", "bichos"},
        boost_columns={
            "taxon_class": ["insecta"],
            "search_document": ["insecto", "insect", "bicho"],
        },
        boost_value=0.07,
    ),
]


SYNONYM_GROUPS = {
    "animal": "animalia animales fauna organismo especie",
    "bicho": "insecto insecta animal pequeño",
    "bichos": "insectos insecta animales pequeños",

    "pajaro": "pájaro ave aves bird birds alas plumas",
    "pájaro": "pajaro ave aves bird birds alas plumas",
    "pajaros": "pájaros ave aves bird birds alas plumas",
    "pájaros": "pajaros ave aves bird birds alas plumas",
    "ave": "aves pajaro bird alas plumas",
    "aves": "ave pajaros birds alas plumas",
    "bird": "ave pajaro aves",
    "birds": "aves pajaros",

    "rosa": "rosado pink flamenco flamingo phoenicopterus roseus",
    "rosado": "rosa pink flamenco flamingo phoenicopterus roseus",
    "pink": "rosa rosado flamenco flamingo phoenicopterus roseus",
    "flamenco": "flamingo phoenicopterus roseus pajaro rosa ave rosa humedal",
    "flamingo": "flamenco phoenicopterus roseus pink bird",

    "polar": "arctic artico ártico hielo ice nieve snow ursus maritimus oso polar polar bear",
    "hielo": "ice polar arctic artico ártico nieve snow ursus maritimus oso polar",
    "ice": "hielo polar arctic ursus maritimus polar bear",
    "oso": "ursus bear mammalia oso polar polar bear",
    "bear": "oso ursus mammalia polar bear",
    "ursus": "ursus maritimus oso polar polar bear",

    "mariposa": "mariposas lepidoptera insecta butterfly butterflies polilla moth alas colores",
    "mariposas": "mariposa lepidoptera insecta butterfly butterflies polillas moths alas colores",
    "butterfly": "mariposa mariposas lepidoptera insecta butterflies",
    "butterflies": "mariposas mariposa lepidoptera insecta butterfly",
    "polilla": "polillas moth moths lepidoptera insecta mariposa",
    "polillas": "polilla moth moths lepidoptera insecta mariposas",
    "moth": "polilla lepidoptera insecta mariposa",
    "moths": "polillas lepidoptera insecta mariposas",
    "lepidoptera": "mariposa mariposas butterfly butterflies polilla moth insecta",

    "rana": "ranas anfibio anfibios amphibia frog frogs agua rio río charca",
    "ranas": "rana anfibio anfibios amphibia frog frogs agua rio río charca",
    "anfibio": "anfibios amphibia rana frog agua",
    "anfibios": "anfibio amphibia ranas frogs agua",
    "frog": "rana amphibia anfibio agua",
    "frogs": "ranas amphibia anfibios agua",
    "rio": "río agua dulce rana anfibio amphibia",
    "río": "rio agua dulce rana anfibio amphibia",
    "agua": "rio río humedal rana pez anfibio",

    "rapaz": "rapaces ave rapaz aguila águila eagle hawk halcon halcón accipitridae montaña",
    "rapaces": "rapaz aves rapaces aguilas eagles hawks accipitridae",
    "aguila": "águila eagle ave rapaz accipitridae aquila montaña",
    "águila": "aguila eagle ave rapaz accipitridae aquila montaña",
    "eagle": "aguila águila ave rapaz accipitridae",
    "hawk": "halcon halcón ave rapaz accipitridae",
    "montana": "montaña mountain ave rapaz aguila",
    "montaña": "montana mountain ave rapaz aguila",

    "planta": "plantas plantae vegetal flor flores flowering plant",
    "plantas": "planta plantae vegetal flor flores flowering plants",
    "flor": "flores planta plantae magnoliopsida flowering flower",
    "flores": "flor planta plantae magnoliopsida flowering flowers",
    "flower": "flor planta flowering",
    "flowers": "flores plantas flowering",

    "mamifero": "mamífero mammalia mammal mamiferos",
    "mamífero": "mamifero mammalia mammal mamiferos",
    "mamiferos": "mamíferos mammalia mammals",
    "mamíferos": "mamiferos mammalia mammals",
    "mammal": "mamifero mammalia",
    "mammals": "mamiferos mammalia",

    "pez": "peces fish actinopterygii agua acuatico",
    "peces": "pez fish actinopterygii agua acuatico",
    "fish": "pez peces actinopterygii agua",
}


def normalize_text(text: str) -> str:
    """Normaliza texto para búsqueda."""
    normalized = unicodedata.normalize("NFKD", str(text).lower())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9ñ\s]", " ", without_accents).strip()


def expand_query(query_text: str) -> str:
    """Expande la consulta con sinónimos e intenciones."""
    normalized_query = normalize_text(query_text)
    words = normalized_query.split()
    expansions = [normalized_query]

    for word in words:
        if word in SYNONYM_GROUPS:
            expansions.append(SYNONYM_GROUPS[word])

    detected_intents = detect_intents(query_text)

    for intent in detected_intents:
        expansions.append(" ".join(sorted(intent.terms)))

    return " ".join(expansions)


def detect_intents(query_text: str) -> list[SearchIntent]:
    """Detecta intenciones de búsqueda por palabras del usuario."""
    normalized_query = normalize_text(query_text)
    query_words = set(normalized_query.split())

    detected = []

    for intent in INTENT_DEFINITIONS:
        normalized_terms = {normalize_text(term) for term in intent.terms}

        if query_words & normalized_terms:
            detected.append(intent)

    return detected


def semantic_search_encyclopedia(
    encyclopedia_df: pd.DataFrame,
    query_text: str,
    top_n: int = 20,
) -> pd.DataFrame:
    """
    Búsqueda híbrida:
    - TF-IDF de palabras;
    - TF-IDF de caracteres para tolerar formas aproximadas;
    - boosts taxonómicos por intención.
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

    result_df["search_score"] = (word_scores * 0.75) + (char_scores * 0.25)
    result_df = apply_intent_boosts(result_df, query_text)

    result_df = result_df[result_df["search_score"] > 0.004]

    return (
        result_df
        .sort_values(["search_score", "observations"], ascending=[False, False])
        .head(top_n)
        .reset_index(drop=True)
    )


def compute_tfidf_scores(
    documents: pd.Series,
    query: str,
    analyzer: str,
    ngram_range: tuple[int, int],
) -> pd.Series:
    """Calcula similitud TF-IDF."""
    vectorizer = TfidfVectorizer(
        analyzer=analyzer,
        ngram_range=ngram_range,
        strip_accents="unicode",
    )

    matrix = vectorizer.fit_transform(list(documents) + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

    return pd.Series(scores, index=documents.index)


def apply_intent_boosts(result_df: pd.DataFrame, query_text: str) -> pd.DataFrame:
    """Aplica boosts según intención detectada."""
    boosted_df = result_df.copy()
    detected_intents = detect_intents(query_text)

    for intent in detected_intents:
        mask = build_intent_mask(boosted_df, intent)

        if mask.any():
            boosted_df.loc[mask, "search_score"] += intent.boost_value

    boosted_df = apply_contradiction_penalties(boosted_df, query_text)

    return boosted_df


def build_intent_mask(df: pd.DataFrame, intent: SearchIntent) -> pd.Series:
    """Construye máscara para una intención."""
    mask = pd.Series(False, index=df.index)

    for column, values in intent.boost_columns.items():
        column_text = get_text_column(df, column).apply(normalize_text)

        for value in values:
            normalized_value = normalize_text(value)
            mask = mask | column_text.str.contains(
                re.escape(normalized_value),
                case=False,
                na=False,
                regex=True,
            )

    return mask


def apply_contradiction_penalties(df: pd.DataFrame, query_text: str) -> pd.DataFrame:
    """Reduce resultados claramente contradictorios."""
    penalized_df = df.copy()
    normalized_query = normalize_text(query_text)
    query_words = set(normalized_query.split())

    plant_words = {"planta", "plantas", "flor", "flores", "vegetal", "flower", "flowers"}
    animal_words = {"animal", "pajaro", "ave", "oso", "rana", "mariposa", "insecto", "pez", "mamifero", "mamífero"}

    if query_words & animal_words and not query_words & plant_words:
        plant_mask = get_text_column(penalized_df, "kingdom").str.lower().eq("plantae")
        penalized_df.loc[plant_mask, "search_score"] *= 0.45

    if query_words & plant_words and not query_words & animal_words:
        animal_mask = get_text_column(penalized_df, "kingdom").str.lower().eq("animalia")
        penalized_df.loc[animal_mask, "search_score"] *= 0.55

    return penalized_df


def get_text_column(df: pd.DataFrame, column: str) -> pd.Series:
    """Devuelve una columna textual aunque no exista."""
    if column not in df.columns:
        return pd.Series([""] * len(df), index=df.index)

    return df[column].fillna("").astype(str)


def build_fallback_document(row: pd.Series) -> str:
    """Crea documento de búsqueda si falta search_document."""
    columns = [
        "scientific_name",
        "kingdom",
        "phylum",
        "taxon_class",
        "taxon_order",
        "family",
        "genus",
        "species",
        "source_queries",
        "profile_text",
    ]

    return " ".join(str(row.get(column, "")) for column in columns)
