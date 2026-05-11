"""Búsqueda semántica inteligente, multilingüe y con precisión taxonómica."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class SearchIntent:
    """Configuración de una intención de búsqueda."""

    name: str
    terms: set[str]
    boost_columns: dict[str, list[str]]
    boost_value: float
    precision_columns: dict[str, list[str]]
    precision: bool = True


GENERIC_BEAR_TERMS = {
    "oso", "osos", "bear", "bears", "ursus",
    "медведь", "медведи",
    "ведмідь", "ведмеді",
    "urso", "ursos",
    "orso", "orsi",
}

POLAR_TERMS = {
    "polar", "hielo", "ice", "artico", "artico", "ártico", "arctic", "nieve", "snow",
    "белый", "белая", "полярный", "полярная", "арктический", "арктическая",
    "білий", "біла", "полярний", "полярна", "арктичний", "арктична",
    "gelo", "neve", "ghiaccio",
}

INTENT_DEFINITIONS = [
    SearchIntent(
        name="polar_bear",
        terms=POLAR_TERMS,
        boost_columns={
            "scientific_name": ["ursus maritimus"],
            "source_queries": ["polar_bear"],
            "search_document": ["oso polar", "polar bear", "animal polar", "hielo", "білий ведмідь", "urso polar", "orso polare", "белый медведь"],
        },
        boost_value=0.24,
        precision_columns={
            "scientific_name": ["ursus maritimus"],
            "source_queries": ["polar_bear"],
            "search_document": ["oso polar", "polar bear", "animal polar"],
        },
    ),
    SearchIntent(
        name="bear",
        terms=GENERIC_BEAR_TERMS,
        boost_columns={
            "family": ["ursidae"],
            "genus": ["ursus"],
            "scientific_name": ["ursus"],
            "search_document": ["oso", "bear", "ursus", "ведмідь", "медведь", "urso", "orso"],
        },
        boost_value=0.22,
        precision_columns={
            "family": ["ursidae"],
            "genus": ["ursus"],
            "scientific_name": ["ursus"],
        },
    ),
    SearchIntent(
        name="butterfly",
        terms={
            "mariposa", "mariposas", "butterfly", "butterflies", "polilla", "polillas", "moth", "moths", "lepidoptera",
            "бабочка", "бабочки", "мотылек", "мотыльки",
            "метелик", "метелики", "міль",
            "borboleta", "borboletas",
            "farfalla", "farfalle", "falena", "falene",
        },
        boost_columns={
            "taxon_order": ["lepidoptera"],
            "source_queries": ["butterflies_lepidoptera"],
            "search_document": ["mariposa", "butterfly", "polilla", "lepidoptera", "метелик", "borboleta", "farfalla", "бабочка"],
        },
        boost_value=0.22,
        precision_columns={
            "taxon_order": ["lepidoptera"],
            "source_queries": ["butterflies_lepidoptera"],
            "search_document": ["lepidoptera", "mariposa", "butterfly", "polilla"],
        },
    ),
    SearchIntent(
        name="amphibian",
        terms={
            "rana", "ranas", "anfibio", "anfibios", "frog", "frogs", "rio", "río", "agua", "charca",
            "лягушка", "лягушки", "жаба", "жабы", "река", "вода",
            "жаби", "річка",
            "sapo", "sapos", "rã", "rãs", "anfíbio", "anfibio",
            "rane", "rospo", "rospi", "fiume", "acqua",
        },
        boost_columns={
            "taxon_class": ["amphibia"],
            "source_queries": ["amphibians"],
            "search_document": ["rana", "anfibio", "frog", "agua", "жаба", "sapo", "rã", "rospo"],
        },
        boost_value=0.18,
        precision_columns={
            "taxon_class": ["amphibia"],
            "source_queries": ["amphibians"],
            "search_document": ["amphibia", "rana", "frog", "anfibio"],
        },
    ),
    SearchIntent(
        name="raptor",
        terms={
            "rapaz", "rapaces", "aguila", "águila", "eagle", "hawk", "halcon", "halcón", "montaña",
            "орел", "орёл", "ястреб", "сокол", "хищная", "гора",
            "яструб", "сокіл", "хижий",
            "águia", "aguia", "falcão", "falcao", "ave de rapina", "montanha",
            "aquila", "falco", "rapace", "rapaci", "montagna",
        },
        boost_columns={
            "family": ["accipitridae"],
            "source_queries": ["raptors_accipitridae"],
            "search_document": ["ave rapaz", "eagle", "aguila", "águila", "montaña", "орел", "águia", "aquila"],
        },
        boost_value=0.18,
        precision_columns={
            "family": ["accipitridae"],
            "source_queries": ["raptors_accipitridae"],
            "search_document": ["ave rapaz", "raptor", "eagle", "aguila", "aquila", "accipitridae"],
        },
    ),
    SearchIntent(
        name="pink_bird",
        terms={
            "flamenco", "flamingo", "rosa", "rosado", "pink",
            "розовый", "розовая", "рожевий", "рожева",
        },
        boost_columns={
            "scientific_name": ["phoenicopterus roseus"],
            "source_queries": ["flamingo_pink_bird"],
            "search_document": ["flamenco", "flamingo", "pajaro rosa", "ave rosa", "pink bird", "рожевий птах", "pássaro rosa", "uccello rosa"],
        },
        boost_value=0.16,
        precision_columns={
            "scientific_name": ["phoenicopterus roseus"],
            "source_queries": ["flamingo_pink_bird"],
            "search_document": ["flamenco", "flamingo", "pajaro rosa", "ave rosa"],
        },
    ),
    SearchIntent(
        name="bird",
        terms={
            "pajaro", "pájaro", "pajaros", "pájaros", "ave", "aves", "bird", "birds",
            "птица", "птицы", "птах", "птахи",
            "passaro", "pássaro", "passaros", "pássaros",
            "uccello", "uccelli",
        },
        boost_columns={
            "taxon_class": ["aves"],
            "search_document": ["bird", "ave", "pajaro", "pájaro", "птица", "птах", "passaro", "pássaro", "uccello"],
        },
        boost_value=0.10,
        precision_columns={
            "taxon_class": ["aves"],
        },
    ),
    SearchIntent(
        name="flowering_plant",
        terms={
            "flor", "flores", "flower", "flowers", "цветок", "цветы", "квітка", "квіти", "fiore", "fiori",
        },
        boost_columns={
            "kingdom": ["plantae"],
            "taxon_class": ["magnoliopsida", "liliopsida"],
            "source_queries": ["flowering_plants"],
            "search_document": ["flor", "flower", "flowering", "квітка", "fiore"],
        },
        boost_value=0.14,
        precision_columns={
            "kingdom": ["plantae"],
            "source_queries": ["flowering_plants"],
            "search_document": ["flowering", "flor", "flower"],
        },
    ),
    SearchIntent(
        name="plant",
        terms={
            "planta", "plantas", "vegetal", "plant",
            "растение", "растения",
            "рослина", "рослини",
            "pianta", "piante",
        },
        boost_columns={
            "kingdom": ["plantae"],
            "source_queries": ["flowering_plants"],
            "search_document": ["planta", "plant", "рослина", "pianta"],
        },
        boost_value=0.12,
        precision_columns={
            "kingdom": ["plantae"],
        },
    ),
    SearchIntent(
        name="insect",
        terms={
            "insecto", "insectos", "insect", "insects", "bicho", "bichos",
            "насекомое", "насекомые", "комаха", "комахи",
            "inseto", "insetos", "insetto", "insetti",
        },
        boost_columns={
            "taxon_class": ["insecta"],
            "search_document": ["insecto", "insect", "bicho", "комаха", "inseto", "insetto"],
        },
        boost_value=0.08,
        precision_columns={
            "taxon_class": ["insecta"],
        },
    ),
    SearchIntent(
        name="mammal",
        terms={
            "mamifero", "mamífero", "mamiferos", "mamíferos", "mammal", "mammals",
            "млекопитающее", "млекопитающие", "ссавець", "ссавці",
            "mammifero", "mammiferi",
        },
        boost_columns={
            "taxon_class": ["mammalia"],
            "source_queries": ["mammals"],
            "search_document": ["mamifero", "mamífero", "mammal", "ссавець", "mammifero"],
        },
        boost_value=0.08,
        precision_columns={
            "taxon_class": ["mammalia"],
        },
        precision=False,
    ),
]


SYNONYM_GROUPS = {
    # General words
    "animal": "animalia fauna organismo especie",
    "animales": "animalia fauna organismos especies",
    "тварина": "animal animalia fauna",
    "тварини": "animal animalia fauna",
    "животное": "animal animalia fauna",
    "животные": "animal animalia fauna",

    # Bear. Important: do not expand generic bear to all Mammalia.
    "oso": "ursus ursidae bear",
    "osos": "ursus ursidae bears",
    "bear": "ursus ursidae oso",
    "bears": "ursus ursidae osos",
    "ursus": "ursus ursidae oso bear",
    "медведь": "ursus ursidae oso bear",
    "медведи": "ursus ursidae osos bears",
    "ведмідь": "ursus ursidae oso bear",
    "ведмеді": "ursus ursidae osos bears",
    "urso": "ursus ursidae oso bear",
    "ursos": "ursus ursidae osos bears",
    "orso": "ursus ursidae oso bear",
    "orsi": "ursus ursidae osos bears",

    # Polar qualifiers
    "polar": "arctic artico hielo ice nieve snow ursus maritimus oso polar polar bear",
    "hielo": "ice polar arctic ursus maritimus oso polar",
    "ice": "hielo polar arctic ursus maritimus polar bear",
    "белый": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "белая": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "полярный": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "полярная": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "білий": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "біла": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "полярний": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "полярна": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "gelo": "hielo ice polar arctic ursus maritimus",
    "ghiaccio": "hielo ice polar arctic ursus maritimus",

    # Birds
    "pajaro": "pájaro ave aves bird birds alas plumas",
    "pájaro": "pajaro ave aves bird birds alas plumas",
    "pajaros": "pájaros ave aves bird birds alas plumas",
    "pájaros": "pajaros ave aves bird birds alas plumas",
    "ave": "aves pajaro bird alas plumas",
    "aves": "ave pajaros birds alas plumas",
    "bird": "ave pajaro aves",
    "birds": "aves pajaros",
    "птица": "ave bird aves pajaro",
    "птицы": "aves birds pajaros",
    "птах": "ave bird aves pajaro",
    "птахи": "aves birds pajaros",
    "passaro": "pássaro ave bird pajaro",
    "pássaro": "passaro ave bird pajaro",
    "uccello": "ave bird pajaro",
    "uccelli": "aves birds pajaros",

    # Pink/flamingo
    "rosa": "rosado pink flamenco flamingo phoenicopterus roseus",
    "rosado": "rosa pink flamenco flamingo phoenicopterus roseus",
    "pink": "rosa rosado flamenco flamingo phoenicopterus roseus",
    "flamenco": "flamingo phoenicopterus roseus pajaro rosa ave rosa humedal",
    "flamingo": "flamenco phoenicopterus roseus pink bird",
    "розовая": "rosa pink flamenco flamingo ave pajaro",
    "розовый": "rosa pink flamenco flamingo ave pajaro",
    "рожевий": "rosa pink flamenco flamingo ave pajaro",
    "рожева": "rosa pink flamenco flamingo ave pajaro",

    # Butterflies
    "mariposa": "lepidoptera insecta butterfly polilla",
    "mariposas": "lepidoptera insecta butterflies polillas",
    "butterfly": "lepidoptera insecta mariposa",
    "butterflies": "lepidoptera insecta mariposas",
    "polilla": "lepidoptera insecta moth mariposa",
    "moth": "lepidoptera insecta polilla mariposa",
    "бабочка": "lepidoptera mariposa butterfly",
    "бабочки": "lepidoptera mariposas butterflies",
    "метелик": "lepidoptera mariposa butterfly",
    "метелики": "lepidoptera mariposas butterflies",
    "borboleta": "lepidoptera mariposa butterfly",
    "borboletas": "lepidoptera mariposas butterflies",
    "farfalla": "lepidoptera mariposa butterfly",
    "farfalle": "lepidoptera mariposas butterflies",

    # Amphibians
    "rana": "amphibia anfibio frog agua rio",
    "ranas": "amphibia anfibios frogs agua rio",
    "anfibio": "amphibia rana frog agua",
    "anfibios": "amphibia ranas frogs agua",
    "frog": "amphibia rana anfibio agua",
    "frogs": "amphibia ranas anfibios agua",
    "rio": "agua rana amphibia",
    "río": "agua rana amphibia",
    "лягушка": "rana frog amphibia",
    "лягушки": "ranas frogs amphibia",
    "жаба": "rana frog amphibia",
    "жабы": "ranas frogs amphibia",
    "sapo": "rana frog amphibia",
    "rã": "rana frog amphibia",
    "rospo": "rana frog amphibia",

    # Raptors
    "rapaz": "ave rapaz accipitridae aguila eagle hawk",
    "rapaces": "aves rapaces accipitridae aguilas eagles",
    "aguila": "águila eagle ave rapaz accipitridae aquila",
    "águila": "aguila eagle ave rapaz accipitridae aquila",
    "eagle": "aguila ave rapaz accipitridae",
    "hawk": "ave rapaz accipitridae",
    "орел": "aguila eagle ave rapaz accipitridae",
    "орёл": "aguila eagle ave rapaz accipitridae",
    "ястреб": "hawk ave rapaz accipitridae",
    "águia": "aguila eagle ave rapaz accipitridae",
    "aguia": "aguila eagle ave rapaz accipitridae",
    "aquila": "aguila eagle ave rapaz accipitridae",

    # Plants/flowers
    "planta": "plantae plant vegetal",
    "plantas": "plantae plants vegetales",
    "plant": "plantae planta",
    "flor": "plantae flowering flower",
    "flores": "plantae flowering flowers",
    "flower": "plantae flor flowering",
    "flowers": "plantae flores flowering",
    "растение": "plantae planta plant",
    "растения": "plantae plantas plants",
    "цветок": "flor flower plantae",
    "цветы": "flores flowers plantae",
    "рослина": "plantae planta plant",
    "рослини": "plantae plantas plants",
    "квітка": "flor flower plantae",
    "квіти": "flores flowers plantae",
    "pianta": "plantae planta plant",
    "piante": "plantae plantas plants",
    "fiore": "flor flower plantae",
    "fiori": "flores flowers plantae",

    # Broad classes
    "insecto": "insecta insect bicho",
    "insectos": "insecta insects bichos",
    "bicho": "insecta insecto animal pequeño",
    "bichos": "insecta insectos animales pequeños",
    "комаха": "insecta insecto",
    "насекомое": "insecta insecto",
    "inseto": "insecta insecto",
    "insetto": "insecta insecto",
    "mamifero": "mammalia mammal",
    "mamífero": "mammalia mammal",
    "mammal": "mammalia mamifero",
    "ссавець": "mammalia mamifero",
    "mammifero": "mammalia mamifero",
    "pez": "fish actinopterygii agua",
    "fish": "pez actinopterygii agua",
    "рыба": "pez fish actinopterygii",
    "риба": "pez fish actinopterygii",
    "peixe": "pez fish actinopterygii",
    "pesce": "pez fish actinopterygii",
}


def normalize_text(text: str) -> str:
    """Normaliza texto y conserva caracteres cirílicos."""
    normalized = unicodedata.normalize("NFKD", str(text).lower())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-zа-яёіїєґ0-9ñ\s]", " ", without_accents).strip()


def expand_query(query_text: str) -> str:
    """Expande la consulta con sinónimos e intenciones detectadas."""
    normalized_query = normalize_text(query_text)
    words = normalized_query.split()
    expansions = [normalized_query]

    for word in words:
        if word in SYNONYM_GROUPS:
            expansions.append(SYNONYM_GROUPS[word])

    for intent in detect_intents(query_text):
        expansions.append(" ".join(sorted(intent.terms)))

    return " ".join(expansions)


def detect_intents(query_text: str) -> list[SearchIntent]:
    """Detecta intenciones por palabras clave."""
    normalized_query = normalize_text(query_text)
    query_words = set(normalized_query.split())

    detected = []

    for intent in INTENT_DEFINITIONS:
        normalized_terms = {normalize_text(term) for term in intent.terms}

        if query_words & normalized_terms:
            detected.append(intent)

    if query_words & GENERIC_BEAR_TERMS and query_words & POLAR_TERMS:
        polar_intent = get_intent_by_name("polar_bear")

        if polar_intent not in detected:
            detected.append(polar_intent)

    return remove_redundant_intents(detected)


def get_intent_by_name(name: str) -> SearchIntent:
    """Obtiene una intención por nombre."""
    for intent in INTENT_DEFINITIONS:
        if intent.name == name:
            return intent

    raise ValueError(f"Intent desconocido: {name}")


def remove_redundant_intents(intents: list[SearchIntent]) -> list[SearchIntent]:
    """
    Evita intenciones demasiado amplias cuando hay una intención específica.

    Ejemplo:
    - mariposa activa butterfly e insect, pero butterfly es más específico.
    - oso polar activa polar_bear y bear, pero polar_bear es más específico.
    """
    names = {intent.name for intent in intents}

    redundant_map = {
        "polar_bear": {"bear", "mammal"},
        "butterfly": {"insect"},
        "pink_bird": {"bird"},
        "raptor": {"bird"},
        "flowering_plant": {"plant"},
    }

    redundant_names = set()

    for specific_name, broad_names in redundant_map.items():
        if specific_name in names:
            redundant_names.update(broad_names)

    return [intent for intent in intents if intent.name not in redundant_names]


def semantic_search_encyclopedia(
    encyclopedia_df: pd.DataFrame,
    query_text: str,
    top_n: int = 20,
) -> pd.DataFrame:
    """Ejecuta búsqueda híbrida y filtra ruido por intención."""
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

    detected_intents = detect_intents(query_text)
    result_df = apply_intent_boosts(result_df, detected_intents)
    result_df = apply_contradiction_penalties(result_df, query_text)
    result_df = apply_precision_filter(result_df, detected_intents)

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


def apply_intent_boosts(
    result_df: pd.DataFrame,
    detected_intents: list[SearchIntent],
) -> pd.DataFrame:
    """Aplica boosts taxonómicos por intención."""
    boosted_df = result_df.copy()

    for intent in detected_intents:
        mask = build_mask_from_columns(boosted_df, intent.boost_columns)

        if mask.any():
            boosted_df.loc[mask, "search_score"] += intent.boost_value

    return boosted_df


def apply_precision_filter(
    result_df: pd.DataFrame,
    detected_intents: list[SearchIntent],
) -> pd.DataFrame:
    """
    Filtra resultados residuales cuando la intención es clara.

    Si el usuario busca "mariposa", devolvemos Lepidoptera.
    Si busca "ведмідь", devolvemos Ursidae/Ursus.
    Si busca "rana", devolvemos Amphibia.
    """
    if result_df.empty:
        return result_df

    precision_intents = [intent for intent in detected_intents if intent.precision]

    if not precision_intents:
        return apply_relative_threshold(result_df)

    masks = [
        build_mask_from_columns(result_df, intent.precision_columns)
        for intent in precision_intents
    ]

    combined_mask = masks[0].copy()

    for mask in masks[1:]:
        combined_mask = combined_mask | mask

    precise_df = result_df[combined_mask].copy()

    if not precise_df.empty:
        return apply_relative_threshold(precise_df, minimum_score=0.03)

    return apply_relative_threshold(result_df)


def apply_relative_threshold(
    result_df: pd.DataFrame,
    minimum_score: float = 0.004,
) -> pd.DataFrame:
    """Quita resultados con score residual demasiado bajo."""
    if result_df.empty:
        return result_df

    max_score = float(result_df["search_score"].max())

    if max_score <= 0:
        return result_df[result_df["search_score"] > minimum_score]

    threshold = max(minimum_score, max_score * 0.12)

    return result_df[result_df["search_score"] >= threshold]


def build_mask_from_columns(
    df: pd.DataFrame,
    columns_config: dict[str, list[str]],
) -> pd.Series:
    """Construye una máscara a partir de columnas y valores esperados."""
    mask = pd.Series(False, index=df.index)

    for column, values in columns_config.items():
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


def apply_contradiction_penalties(
    df: pd.DataFrame,
    query_text: str,
) -> pd.DataFrame:
    """Penaliza contradicciones generales animal/planta."""
    penalized_df = df.copy()
    normalized_query = normalize_text(query_text)
    query_words = set(normalized_query.split())

    plant_words = {
        "planta", "plantas", "flor", "flores", "vegetal", "flower", "flowers",
        "растение", "растения", "цветок", "цветы",
        "рослина", "рослини", "квітка", "квіти",
        "pianta", "piante", "fiore", "fiori",
    }

    animal_words = {
        "animal", "pajaro", "pájaro", "ave", "oso", "rana", "mariposa", "insecto", "pez", "mamifero", "mamífero",
        "тварина", "животное", "птица", "птах", "медведь", "ведмідь", "жаба", "лягушка", "бабочка", "метелик",
        "passaro", "pássaro", "uccello", "urso", "orso", "sapo", "rã", "farfalla", "borboleta",
    }

    if query_words & animal_words and not query_words & plant_words:
        plant_mask = get_text_column(penalized_df, "kingdom").apply(normalize_text).eq("plantae")
        penalized_df.loc[plant_mask, "search_score"] *= 0.45

    if query_words & plant_words and not query_words & animal_words:
        animal_mask = get_text_column(penalized_df, "kingdom").apply(normalize_text).eq("animalia")
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
