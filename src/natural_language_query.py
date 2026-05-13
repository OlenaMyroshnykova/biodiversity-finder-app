"""Traductor simple de lenguaje natural a máscaras booleanas de Pandas.

Arquitectura limpia para el entregable:
- El vibe-search principal usa español e inglés.
- Los nombres comunes multilingües no participan en filtros estructurados.
- La app convierte frases naturales en columnas normalizadas: size/habitat/color/group.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.search_components.normalizer import normalize_text

SIZE_KEYWORDS = {
    "small": ["small", "little", "tiny", "pequeno", "pequeño", "chico", "mini"],
    "medium": ["medium", "mediano", "mediana"],
    "large": ["large", "big", "grande", "enorme", "gigante"],
}

HABITAT_KEYWORDS = {
    "desert": ["desert", "desierto", "arid", "arido", "árido"],
    "wetland": ["wetland", "humedal", "water", "agua", "river", "rio", "río", "lake", "lago"],
    "forest": ["forest", "bosque", "jungle", "selva"],
    "savanna": ["savanna", "sabana", "savana"],
    "mountain": ["mountain", "montana", "montaña"],
    "polar": ["polar", "ice", "hielo", "arctic", "artico", "ártico"],
    "meadow": ["meadow", "pradera", "garden", "jardin", "jardín"],
    "ocean": ["ocean", "sea", "marine", "oceano", "océano", "mar", "marino"],
}

COLOR_KEYWORDS = {
    "pink": ["pink", "rosa"],
    "white": ["white", "blanco", "blanca"],
    "brown": ["brown", "marron", "marrón", "dorado", "golden"],
    "green": ["green", "verde"],
    "gray": ["gray", "grey", "gris"],
    "black": ["black", "negro", "negra"],
    "colorful": ["colorful", "multicolor", "bright", "colorido", "colores"],
}

GROUP_KEYWORDS = {
    "animal": ["animal", "animals", "animales", "bicho", "criatura", "fauna"],
    "insect": ["insect", "insecto", "bug", "mariposa", "butterfly", "polilla", "moth"],
    "bird": ["bird", "ave", "pajaro", "pájaro", "aves"],
    "mammal": ["mammal", "mamifero", "mamífero", "mamíferos", "mamiferos"],
    "amphibian": ["amphibian", "anfibio", "anfibios", "frog", "rana", "sapo", "toad"],
    "plant": ["plant", "plants", "planta", "plantas", "flower", "flor", "arbol", "árbol", "tree", "vegetal"],
    "reptile": ["reptile", "reptil", "reptiles", "cocodrilo", "crocodile", "caiman", "caimán", "lagarto", "lizard", "serpiente", "snake", "iguana"],
    "fish": ["fish", "pez", "peces", "tiburon", "tiburón", "shark", "raya", "ray"],
    "spider": ["spider", "spiders", "araña", "arañas", "arana", "scorpion", "escorpion", "escorpión", "arachnid", "aracnido", "arácnido"],
}

GROUP_TO_TAXON_TEXT = {
    "animal": ["animalia"],
    "insect": ["insecta", "lepidoptera"],
    "bird": ["aves"],
    "mammal": ["mammalia"],
    "amphibian": ["amphibia"],
    "plant": ["plantae", "magnoliopsida", "liliopsida", "pinopsida", "polypodiopsida"],
    "reptile": ["reptilia", "crocodylia", "squamata"],
    "fish": ["actinopterygii", "chondrichthyes", "pisces", "teleostei"],
    "spider": ["arachnida", "araneae", "scorpiones"],
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
        return bool(self.size_tags or self.habitat_tags or self.color_tags or self.group_tags)


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


def detect_tags(normalized_query: str, vocabulary: dict[str, list[str]]) -> list[str]:
    """Detecta tags por vocabulario controlado."""
    detected: list[str] = []
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
) -> tuple[pd.DataFrame, ParsedNaturalQuery, bool]:
    """Aplica filtros con df.loc según la frase natural."""
    parsed_query = parse_natural_language_query(query_text)
    if df.empty or not parsed_query.has_structured_filters:
        return df.copy(), parsed_query, False

    mask = pd.Series(True, index=df.index)

    if parsed_query.size_tags and "size_tag" in df.columns:
        mask &= build_contains_mask(df["size_tag"], parsed_query.size_tags)
    if parsed_query.habitat_tags and "habitat_tag" in df.columns:
        mask &= build_contains_mask(df["habitat_tag"], parsed_query.habitat_tags)
    if parsed_query.color_tags and "color_tag" in df.columns:
        mask &= build_contains_mask(df["color_tag"], parsed_query.color_tags)
    if parsed_query.group_tags:
        mask &= build_group_mask(df, parsed_query.group_tags)

    filtered_df = df.loc[mask].copy()
    if filtered_df.empty:
        return df.copy(), parsed_query, True
    return filtered_df, parsed_query, False


def build_group_mask(df: pd.DataFrame, group_tags: list[str]) -> pd.Series:
    """Construye máscara para grupos sin usar common names multilingües."""
    group_mask = pd.Series(False, index=df.index)
    taxon_columns = [
        column
        for column in ["kingdom", "taxon_class", "taxon_order", "family", "phylum"]
        if column in df.columns
    ]
    if not taxon_columns:
        return pd.Series(True, index=df.index)

    for group_tag in group_tags:
        expected_terms = GROUP_TO_TAXON_TEXT.get(group_tag, [group_tag])
        for column in taxon_columns:
            group_mask |= build_contains_mask(df[column], expected_terms)
    return group_mask


def build_contains_mask(series: pd.Series, tags: list[str]) -> pd.Series:
    """Construye máscara OR para una lista de tags."""
    normalized_series = series.fillna("").astype(str).apply(normalize_text)
    mask = pd.Series(False, index=series.index)
    for tag in tags:
        normalized_tag = normalize_text(tag)
        mask |= normalized_series.str.contains(normalized_tag, regex=False, na=False)
    return mask
