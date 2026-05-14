"""Traductor simple de lenguaje natural a máscaras booleanas de Pandas.

Arquitectura para el entregable:
- El vibe-search principal usa español e inglés.
- Los nombres comunes multilingües no participan en filtros estructurados.
- La app convierte frases naturales en columnas normalizadas: size/habitat/color/group.
- Si el filtro exacto no existe en el artifact, se relaja de forma controlada sin
  caer en una búsqueda textual aleatoria que contradiga el hábitat pedido.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

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
    "savanna": ["savanna", "sabana", "savana", "grassland", "pradera"],
    "mountain": ["mountain", "montana", "montaña"],
    "polar": ["polar", "ice", "hielo", "arctic", "artico", "ártico"],
    "meadow": ["meadow", "pradera", "garden", "jardin", "jardín"],
    "ocean": ["ocean", "sea", "marine", "oceano", "océano", "mar", "marino"],
}

# Términos equivalentes o próximos para no devolver 0 cuando el artifact usa
# "grassland/pradera" en vez de "savanna/sabana". Se mantiene el sentido ecológico.
HABITAT_RELATED_TERMS = {
    "savanna": ["savanna", "savana", "sabana", "grassland", "grasslands", "prairie", "pradera", "meadow"],
    "desert": ["desert", "desierto", "arid", "arido", "árido"],
    "wetland": ["wetland", "humedal", "water", "agua", "river", "rio", "río", "lake", "lago"],
    "forest": ["forest", "bosque", "jungle", "selva", "woodland"],
    "mountain": ["mountain", "montana", "montaña", "alpine"],
    "polar": ["polar", "ice", "hielo", "arctic", "artico", "ártico", "tundra"],
    "meadow": ["meadow", "pradera", "grassland", "garden", "jardin", "jardín"],
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

STRUCTURED_VOCABULARIES = [
    SIZE_KEYWORDS,
    HABITAT_KEYWORDS,
    COLOR_KEYWORDS,
    GROUP_KEYWORDS,
]

# Palabras funcionales que quedan cuando quitamos filtros estructurados de una
# frase como "animal grande de la sabana". No deben alimentar el fallback textual.
REMAINING_TEXT_STOPWORDS = {
    "a", "an", "the", "of", "in", "on", "at", "from", "with", "and", "or",
    "un", "una", "unos", "unas", "el", "la", "los", "las", "de", "del",
    "al", "en", "con", "y", "o", "que", "vive", "viven", "por", "para",
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

    @property
    def status_message(self) -> str:
        """Mensaje estable para la UI.

        Se deja como propiedad para que app.py pueda mostrar feedback sin depender
        de atributos temporales. Esto corrige el AttributeError visto en Streamlit.
        """
        if not self.has_structured_filters:
            return "No se detectaron filtros estructurados. Se usa búsqueda por nombre/texto."
        detected = []
        if self.size_tags:
            detected.append(f"tamaño: {', '.join(self.size_tags)}")
        if self.habitat_tags:
            detected.append(f"hábitat: {', '.join(self.habitat_tags)}")
        if self.color_tags:
            detected.append(f"color: {', '.join(self.color_tags)}")
        if self.group_tags:
            detected.append(f"grupo: {', '.join(self.group_tags)}")
        return "Filtros detectados: " + " · ".join(detected)


def parse_natural_language_query(query_text: str) -> ParsedNaturalQuery:
    """Extrae filtros estructurados de la frase del usuario.

    Punto importante de arquitectura: las palabras ya usadas como filtros
    estructurados no pueden reutilizarse como búsqueda textual secundaria.
    Ejemplo: "animal grande de la sabana" debe producir filtros
    ``animal + large + savanna`` y ``remaining_text == ""``. Así evitamos que
    "grande" encuentre por accidente una especie llamada "Rana Grande".
    """
    normalized_query = normalize_text(query_text)
    size_tags = detect_tags(normalized_query, SIZE_KEYWORDS)
    habitat_tags = detect_tags(normalized_query, HABITAT_KEYWORDS)
    color_tags = detect_tags(normalized_query, COLOR_KEYWORDS)
    group_tags = detect_tags(normalized_query, GROUP_KEYWORDS)

    return ParsedNaturalQuery(
        size_tags=size_tags,
        habitat_tags=habitat_tags,
        color_tags=color_tags,
        group_tags=group_tags,
        remaining_text=build_remaining_text(
            normalized_query=normalized_query,
            detected_tags_by_vocabulary=[
                (SIZE_KEYWORDS, size_tags),
                (HABITAT_KEYWORDS, habitat_tags),
                (COLOR_KEYWORDS, color_tags),
                (GROUP_KEYWORDS, group_tags),
            ],
        ),
    )


def build_remaining_text(
    *,
    normalized_query: str,
    detected_tags_by_vocabulary: list[tuple[dict[str, list[str]], list[str]]],
) -> str:
    """Elimina del fallback textual las palabras ya convertidas en filtros.

    Mantiene nombres científicos o términos específicos que no forman parte del
    vocabulario estructurado, por ejemplo "panthera leo grande" ->
    "panthera leo".
    """
    remaining = f" {normalized_query} "

    for vocabulary, detected_tags in detected_tags_by_vocabulary:
        for tag in detected_tags:
            for keyword in vocabulary.get(tag, []):
                normalized_keyword = normalize_text(keyword).strip()
                if not normalized_keyword:
                    continue
                pattern = rf"(?<!\w){re.escape(normalized_keyword)}(?!\w)"
                remaining = re.sub(pattern, " ", remaining)

    tokens = [
        token
        for token in remaining.split()
        if token and token not in REMAINING_TEXT_STOPWORDS
    ]
    return " ".join(tokens)


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
    """Aplica filtros con df.loc según la frase natural.

    El tercer valor indica si se usó relajación controlada o si no hubo resultados
    exactos. Importante: si hay filtros estructurados, nunca devolvemos todo el
    dataset como fallback, porque eso genera resultados contradictorios.
    """
    parsed_query = parse_natural_language_query(query_text)
    if df.empty:
        return df.copy(), parsed_query, False
    if not parsed_query.has_structured_filters:
        return df.copy(), parsed_query, False

    exact_mask = build_structured_mask(
        df=df,
        parsed_query=parsed_query,
        include_size=True,
        include_color=True,
        broaden_habitat=False,
    )
    exact_df = df.loc[exact_mask].copy()
    if not exact_df.empty:
        return exact_df, parsed_query, False

    # Relajación controlada: mantener grupo y hábitat; relajar tamaño/color,
    # porque suelen ser inferencias más débiles en el dataset.
    relaxed_mask = build_structured_mask(
        df=df,
        parsed_query=parsed_query,
        include_size=False,
        include_color=False,
        broaden_habitat=True,
    )
    relaxed_df = df.loc[relaxed_mask].copy()
    if not relaxed_df.empty:
        return relaxed_df, parsed_query, True

    return df.iloc[0:0].copy(), parsed_query, True


def build_structured_mask(
    df: pd.DataFrame,
    parsed_query: ParsedNaturalQuery,
    *,
    include_size: bool,
    include_color: bool,
    broaden_habitat: bool,
) -> pd.Series:
    """Construye una máscara estructurada estable."""
    mask = pd.Series(True, index=df.index)

    if include_size and parsed_query.size_tags:
        mask &= build_multi_column_contains_mask(
            df,
            columns=["size_tag", "tags_de_busqueda"],
            tags=parsed_query.size_tags,
        )

    if parsed_query.habitat_tags:
        habitat_terms: list[str] = []
        for tag in parsed_query.habitat_tags:
            if broaden_habitat:
                habitat_terms.extend(HABITAT_RELATED_TERMS.get(tag, [tag]))
            else:
                habitat_terms.append(tag)
        mask &= build_multi_column_contains_mask(
            df,
            columns=["habitat_tag", "tags_de_busqueda", "search_document"],
            tags=habitat_terms,
        )

    if include_color and parsed_query.color_tags:
        mask &= build_multi_column_contains_mask(
            df,
            columns=["color_tag", "tags_de_busqueda"],
            tags=parsed_query.color_tags,
        )

    if parsed_query.group_tags:
        mask &= build_group_mask(df, parsed_query.group_tags)

    return mask


def build_group_mask(df: pd.DataFrame, group_tags: list[str]) -> pd.Series:
    """Construye máscara para grupos sin usar common names multilingües."""
    group_mask = pd.Series(False, index=df.index)
    taxon_columns = [
        column
        for column in ["kingdom", "taxon_class", "taxon_order", "family", "phylum", "search_document"]
        if column in df.columns
    ]
    if not taxon_columns:
        return pd.Series(True, index=df.index)

    for group_tag in group_tags:
        expected_terms = GROUP_TO_TAXON_TEXT.get(group_tag, [group_tag])
        for column in taxon_columns:
            group_mask |= build_contains_mask(df[column], expected_terms)
    return group_mask


def build_multi_column_contains_mask(
    df: pd.DataFrame,
    columns: list[str],
    tags: list[str],
) -> pd.Series:
    """Construye una máscara OR buscando tags en varias columnas existentes."""
    existing_columns = [column for column in columns if column in df.columns]
    if not existing_columns:
        return pd.Series(True, index=df.index)

    mask = pd.Series(False, index=df.index)
    for column in existing_columns:
        mask |= build_contains_mask(df[column], tags)
    return mask


def build_contains_mask(series: pd.Series, tags: list[str]) -> pd.Series:
    """Construye máscara OR para una lista de tags."""
    normalized_series = series.fillna("").astype(str).apply(normalize_text)
    mask = pd.Series(False, index=series.index)
    for tag in tags:
        normalized_tag = normalize_text(tag)
        mask |= normalized_series.str.contains(normalized_tag, regex=False, na=False)
    return mask
