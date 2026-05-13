"""Translator from natural language to Pandas boolean masks.

The stable demo search supports Spanish and English. Other common names can be
shown in cards and used by fallback name search, but the main vibe-search only
uses structured tags: size, habitat, color and group.
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
    "black": ["black", "negro", "negra"],
    "grey": ["grey", "gray", "gris"],
    "colorful": ["colorful", "multicolor", "bright", "colorido", "colores"],
}

GROUP_KEYWORDS = {
    "animal": ["animal", "animals", "animales", "bicho", "criatura"],
    "insect": ["insect", "insecto", "bug", "mariposa", "butterfly", "moth", "polilla"],
    "bird": ["bird", "birds", "ave", "aves", "pajaro", "pájaro"],
    "mammal": ["mammal", "mammals", "mamifero", "mamífero", "mamiferos", "mamíferos"],
    "amphibian": ["amphibian", "anfibio", "anfibios", "frog", "rana", "sapo", "toad"],
    "plant": ["plant", "plants", "planta", "plantas", "flower", "flor", "arbol", "árbol", "tree"],
    "reptile": ["reptile", "reptiles", "reptil", "reptilia", "cocodrilo", "crocodile", "snake", "serpiente", "lizard", "lagarto"],
    "fish": ["fish", "pez", "peces", "shark", "tiburon", "tiburón", "ray", "raya"],
    "spider": ["spider", "spiders", "araña", "arañas", "arana", "scorpion", "escorpion", "escorpión", "arachnid"],
    "fungi": ["fungi", "fungus", "hongo", "hongos", "seta", "setas", "mushroom", "mushrooms"],
}

GROUP_TO_TAXON_TERMS = {
    "animal": ["animalia"],
    "insect": ["insecta", "lepidoptera", "papilionidae"],
    "bird": ["aves", "accipitridae", "anatidae", "laridae"],
    "mammal": ["mammalia"],
    "amphibian": ["amphibia", "anura"],
    "plant": ["plantae", "magnoliopsida"],
    "reptile": ["reptilia", "crocodylia", "serpentes", "lacertilia"],
    "fish": ["actinopterygii", "chondrichthyes", "teleostei", "selachimorpha"],
    "spider": ["arachnida", "araneae", "scorpiones"],
    "fungi": ["fungi", "basidiomycota", "ascomycota"],
}

GROUP_FILTER_COLUMNS = ["kingdom", "taxon_class", "taxon_order", "family", "genus"]


@dataclass(frozen=True)
class ParsedNaturalQuery:
    """Structured result of the natural-language translator."""

    size_tags: list[str]
    habitat_tags: list[str]
    color_tags: list[str]
    group_tags: list[str]
    remaining_text: str

    @property
    def has_structured_filters(self) -> bool:
        """Return True when at least one structured filter is detected."""

        return bool(self.size_tags or self.habitat_tags or self.color_tags or self.group_tags)


def parse_natural_language_query(query_text: str) -> ParsedNaturalQuery:
    """Extract structured filters from the user's phrase."""

    normalized_query = normalize_text(query_text)
    return ParsedNaturalQuery(
        size_tags=detect_tags(normalized_query, SIZE_KEYWORDS),
        habitat_tags=detect_tags(normalized_query, HABITAT_KEYWORDS),
        color_tags=detect_tags(normalized_query, COLOR_KEYWORDS),
        group_tags=detect_tags(normalized_query, GROUP_KEYWORDS),
        remaining_text=normalized_query,
    )


def detect_tags(normalized_query: str, vocabulary: dict[str, list[str]]) -> list[str]:
    """Detect canonical tags by controlled vocabulary."""

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
    """Apply df.loc filters from the natural-language phrase.

    Returns ``(result_df, parsed_query, fallback_used)``. When structured
    filters are detected but no rows match, the original dataframe is returned
    so that the text fallback search can still operate.
    """

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


def build_contains_mask(series: pd.Series, tags: list[str]) -> pd.Series:
    """Build an OR mask for a list of canonical tags."""

    normalized_series = series.fillna("").astype(str).apply(normalize_text)
    mask = pd.Series(False, index=series.index)
    for tag in tags:
        normalized_tag = normalize_text(tag)
        mask |= normalized_series.str.contains(normalized_tag, regex=False, na=False)
    return mask


def build_group_mask(df: pd.DataFrame, group_tags: list[str]) -> pd.Series:
    """Build group mask from taxonomy columns, not from noisy common names."""

    group_mask = pd.Series(False, index=df.index)
    existing_columns = [column for column in GROUP_FILTER_COLUMNS if column in df.columns]
    if not existing_columns:
        return pd.Series(True, index=df.index)

    for group_tag in group_tags:
        taxon_terms = GROUP_TO_TAXON_TERMS.get(group_tag, [group_tag])
        for column in existing_columns:
            group_mask |= build_contains_mask(df[column], taxon_terms)

    return group_mask
