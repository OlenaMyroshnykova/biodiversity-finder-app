"""Traductor simple de lenguaje natural a máscaras booleanas de Pandas."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.search_components.normalizer import normalize_text


SIZE_KEYWORDS = {
    "small": [
        "small",
        "little",
        "tiny",
        "pequeno",
        "pequeño",
        "chico",
        "mini",
        "bicho",
        "insecto",
        "bug",
    ],
    "medium": ["medium", "mediano", "mediana"],
    "large": ["large", "big", "grande", "enorme", "gigante"],
}

HABITAT_KEYWORDS = {
    "desert": ["desert", "desierto", "arid", "arido", "árido"],
    "wetland": [
        "wetland",
        "humedal",
        "water",
        "agua",
        "river",
        "rio",
        "río",
        "lake",
        "lago",
    ],
    "forest": ["forest", "bosque", "jungle", "selva"],
    "savanna": ["savanna", "sabana"],
    "mountain": ["mountain", "montana", "montaña"],
    "polar": ["polar", "ice", "hielo", "arctic", "artico", "ártico"],
    "meadow": ["meadow", "pradera", "garden", "jardin", "jardín"],
}

COLOR_KEYWORDS = {
    "pink": ["pink", "rosa"],
    "white": ["white", "blanco", "blanca"],
    "brown": ["brown", "marron", "marrón", "dorado", "golden"],
    "green": ["green", "verde"],
    "colorful": ["colorful", "multicolor", "bright", "colorido", "colores"],
}

GROUP_KEYWORDS = {
    "insect": ["insect", "insecto", "bicho", "bug"],
    "bird": ["bird", "ave", "pajaro", "pájaro"],
    "mammal": ["mammal", "mamifero", "mamífero"],
    "amphibian": ["amphibian", "anfibio", "frog", "rana"],
    "plant": ["plant", "planta", "flower", "flor"],
}


@dataclass(frozen=True)
class ParsedNaturalQuery:
    """Resultado del traductor de lenguaje natural."""

    size_tags: list[str]
    habitat_tags: list[str]
    color_tags: list[str]
    group_tags: list[str]
    remaining_text: str

    @property
    def has_structured_filters(self) -> bool:
        """Indica si se detectó al menos un filtro estructurado."""
        return bool(
            self.size_tags
            or self.habitat_tags
            or self.color_tags
            or self.group_tags
        )


def parse_natural_language_query(query_text: str) -> ParsedNaturalQuery:
    """Extrae filtros estructurados de la frase del usuario."""
    normalized_query = normalize_text(query_text)

    return ParsedNaturalQuery(
        size_tags=detect_tags(normalized_query, SIZE_KEYWORDS),
        habitat_tags=detect_tags(normalized_query, HABITAT_KEYWORDS),
        color_tags=detect_tags(normalized_query, COLOR_KEYWORDS),
        group_tags=detect_tags(normalized_query, GROUP_KEYWORDS),
        remaining_text=normalized_query,
    )


def detect_tags(
    normalized_query: str,
    vocabulary: dict[str, list[str]],
) -> list[str]:
    """Detecta tags por vocabulario."""
    detected = []

    query_tokens = set(normalized_query.split())

    for tag, keywords in vocabulary.items():
        normalized_keywords = [normalize_text(keyword) for keyword in keywords]

        if any(keyword in query_tokens for keyword in normalized_keywords):
            detected.append(tag)
            continue

        if any(keyword and keyword in normalized_query for keyword in normalized_keywords):
            detected.append(tag)

    return detected


def apply_natural_language_filters(
    df: pd.DataFrame,
    query_text: str,
) -> tuple[pd.DataFrame, ParsedNaturalQuery]:
    """Aplica filtros con df.loc según la frase natural."""
    parsed_query = parse_natural_language_query(query_text)

    if df.empty or not parsed_query.has_structured_filters:
        return df.copy(), parsed_query

    mask = pd.Series(True, index=df.index)

    if parsed_query.size_tags and "size_tag" in df.columns:
        mask &= build_contains_mask(df["size_tag"], parsed_query.size_tags)

    if parsed_query.habitat_tags and "habitat_tag" in df.columns:
        mask &= build_contains_mask(df["habitat_tag"], parsed_query.habitat_tags)

    if parsed_query.color_tags and "color_tag" in df.columns:
        mask &= build_contains_mask(df["color_tag"], parsed_query.color_tags)

    if parsed_query.group_tags:
        group_columns = [
            column
            for column in ["tags_de_busqueda", "taxon_class", "family", "search_document"]
            if column in df.columns
        ]

        if group_columns:
            group_mask = pd.Series(False, index=df.index)

            for column in group_columns:
                group_mask |= build_contains_mask(df[column], parsed_query.group_tags)

            mask &= group_mask

    filtered_df = df.loc[mask].copy()

    if filtered_df.empty:
        return df.copy(), parsed_query

    return filtered_df, parsed_query


def build_contains_mask(series: pd.Series, tags: list[str]) -> pd.Series:
    """Construye máscara OR para una lista de tags."""
    normalized_series = series.fillna("").astype(str).apply(normalize_text)
    mask = pd.Series(False, index=series.index)

    for tag in tags:
        normalized_tag = normalize_text(tag)
        mask |= normalized_series.str.contains(normalized_tag, regex=False, na=False)

    return mask
