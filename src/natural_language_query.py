"""Translator from natural language to Pandas boolean masks.

Architecture note
-----------------
The natural-language layer is responsible for structured concepts such as
size, habitat, color and broad biological group. These concepts should not be
sent unchanged to the TF-IDF name search, because phrases like "animal grande
de la sabana" can accidentally rank a species whose common name contains only
"Grande".

The module therefore returns two things:
- a strict df.loc result when all detected structured filters match;
- a soft structured ranking used when strict AND filtering finds nothing.
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
    "savanna": ["savanna", "sabana", "savana", "grassland", "pastizal"],
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
STOPWORDS = {
    "un", "una", "unos", "unas", "el", "la", "los", "las", "de", "del", "que",
    "vive", "viven", "en", "con", "y", "o", "por", "para", "tipo", "especie",
}


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
    """Extract structured filters and remove those words from fallback text."""
    normalized_query = normalize_text(query_text)
    size_tags = detect_tags(normalized_query, SIZE_KEYWORDS)
    habitat_tags = detect_tags(normalized_query, HABITAT_KEYWORDS)
    color_tags = detect_tags(normalized_query, COLOR_KEYWORDS)
    group_tags = detect_tags(normalized_query, GROUP_KEYWORDS)

    consumed_words = build_consumed_words(size_tags, SIZE_KEYWORDS)
    consumed_words |= build_consumed_words(habitat_tags, HABITAT_KEYWORDS)
    consumed_words |= build_consumed_words(color_tags, COLOR_KEYWORDS)
    consumed_words |= build_consumed_words(group_tags, GROUP_KEYWORDS)
    consumed_words |= STOPWORDS

    remaining_tokens = [
        token for token in normalized_query.split()
        if token and token not in consumed_words
    ]

    return ParsedNaturalQuery(
        size_tags=size_tags,
        habitat_tags=habitat_tags,
        color_tags=color_tags,
        group_tags=group_tags,
        remaining_text=" ".join(remaining_tokens),
    )


def build_consumed_words(tags: list[str], vocabulary: dict[str, list[str]]) -> set[str]:
    """Return words that were used to detect structured tags."""
    words: set[str] = set()
    for tag in tags:
        words.add(normalize_text(tag))
        for keyword in vocabulary.get(tag, []):
            words.update(normalize_text(keyword).split())
    return words


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
    """Apply strict df.loc filters from the natural-language phrase.

    Returns ``(result_df, parsed_query, fallback_used)``. When strict AND filters
    return nothing, the function returns a soft structured candidate set instead
    of the whole dataframe. This keeps the demo useful without letting generic
    words such as "grande" accidentally rank unrelated names.
    """
    parsed_query = parse_natural_language_query(query_text)
    if df.empty or not parsed_query.has_structured_filters:
        return df.copy(), parsed_query, False

    strict_mask = build_strict_structured_mask(df, parsed_query)
    strict_df = df.loc[strict_mask].copy()
    if not strict_df.empty:
        strict_df["structured_match_score"] = 1.0
        return strict_df, parsed_query, False

    soft_df = build_soft_structured_candidates(df, parsed_query)
    if soft_df.empty:
        return df.iloc[0:0].copy(), parsed_query, True
    return soft_df, parsed_query, True


def build_strict_structured_mask(df: pd.DataFrame, parsed_query: ParsedNaturalQuery) -> pd.Series:
    """Build the original AND mask for exact df.loc filtering."""
    mask = pd.Series(True, index=df.index)
    if parsed_query.size_tags and "size_tag" in df.columns:
        mask &= build_contains_mask(df["size_tag"], parsed_query.size_tags)
    if parsed_query.habitat_tags and "habitat_tag" in df.columns:
        mask &= build_contains_mask(df["habitat_tag"], parsed_query.habitat_tags)
    if parsed_query.color_tags and "color_tag" in df.columns:
        mask &= build_contains_mask(df["color_tag"], parsed_query.color_tags)
    if parsed_query.group_tags:
        mask &= build_group_mask(df, parsed_query.group_tags)
    return mask


def build_soft_structured_candidates(
    df: pd.DataFrame,
    parsed_query: ParsedNaturalQuery,
    *,
    minimum_score: float = 1.0,
) -> pd.DataFrame:
    """Return partial structured matches with an explicit score.

    Weights prioritize more specific signals over the very broad "animal" group:
    habitat > size/color > specific biological group > generic animalia.
    """
    score = pd.Series(0.0, index=df.index)

    if parsed_query.habitat_tags and "habitat_tag" in df.columns:
        score += build_contains_mask(df["habitat_tag"], parsed_query.habitat_tags).astype(float) * 1.6
    if parsed_query.size_tags and "size_tag" in df.columns:
        score += build_contains_mask(df["size_tag"], parsed_query.size_tags).astype(float) * 1.2
    if parsed_query.color_tags and "color_tag" in df.columns:
        score += build_contains_mask(df["color_tag"], parsed_query.color_tags).astype(float) * 1.2
    if parsed_query.group_tags:
        group_weight = 0.4 if parsed_query.group_tags == ["animal"] else 1.1
        score += build_group_mask(df, parsed_query.group_tags).astype(float) * group_weight

    result = df.loc[score >= minimum_score].copy()
    if result.empty:
        return result
    result["structured_match_score"] = score.loc[result.index]
    sort_columns = ["structured_match_score"]
    ascending = [False]
    if "observations" in result.columns:
        sort_columns.append("observations")
        ascending.append(False)
    return result.sort_values(sort_columns, ascending=ascending)


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
