"""Búsqueda semántica inteligente y multilingüe para la enciclopedia."""

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
        terms={
            "pajaro", "pájaro", "pajaros", "pájaros", "ave", "aves", "bird", "birds",
            "птица", "птицы", "птах", "птахи",
            "passaro", "pássaro", "passaros", "pássaros", "ave", "aves",
            "uccello", "uccelli",
        },
        boost_columns={
            "taxon_class": ["aves"],
            "search_document": ["bird", "ave", "pajaro", "pájaro", "птица", "птах", "passaro", "pássaro", "uccello"],
        },
        boost_value=0.08,
    ),
    SearchIntent(
        name="pink_flamingo",
        terms={
            "flamenco", "flamingo", "rosa", "rosado", "pink",
            "розовый", "розовая", "рожевий", "рожева",
            "rosa", "rosado", "rosada",
        },
        boost_columns={
            "scientific_name": ["phoenicopterus roseus"],
            "search_document": ["flamenco", "flamingo", "pajaro rosa", "ave rosa", "pink bird", "рожевий птах", "pássaro rosa", "uccello rosa"],
        },
        boost_value=0.14,
    ),
    SearchIntent(
        name="polar_bear",
        terms={
            "polar", "hielo", "ice", "oso", "bear", "ursus", "artico", "ártico", "arctic", "nieve",
            "медведь", "медведи", "белый", "полярный", "арктический",
            "ведмідь", "ведмеді", "білий", "полярний", "арктичний",
            "urso", "ursos", "gelo", "neve", "ártico", "artico",
            "orso", "orsi", "ghiaccio", "neve", "artico",
        },
        boost_columns={
            "scientific_name": ["ursus maritimus"],
            "source_queries": ["polar_bear"],
            "search_document": ["oso polar", "polar bear", "animal polar", "hielo", "білий ведмідь", "urso polar", "orso polare", "белый медведь"],
        },
        boost_value=0.20,
    ),
    SearchIntent(
        name="butterfly",
        terms={
            "mariposa", "mariposas", "butterfly", "butterflies", "polilla", "polillas", "moth", "moths", "lepidoptera",
            "бабочка", "бабочки", "мотылек", "мотыльки",
            "метелик", "метелики", "міль",
            "borboleta", "borboletas", "mariposa", "mariposas",
            "farfalla", "farfalle", "falena", "falene",
        },
        boost_columns={
            "taxon_order": ["lepidoptera"],
            "source_queries": ["butterflies_lepidoptera"],
            "search_document": ["mariposa", "butterfly", "polilla", "lepidoptera", "метелик", "borboleta", "farfalla", "бабочка"],
        },
        boost_value=0.20,
    ),
    SearchIntent(
        name="amphibian",
        terms={
            "rana", "ranas", "anfibio", "anfibios", "frog", "frogs", "rio", "río", "agua", "charca",
            "лягушка", "лягушки", "жаба", "жабы", "река", "вода",
            "жаба", "жаби", "річка", "вода",
            "sapo", "sapos", "rã", "rãs", "anfíbio", "anfibio", "rio", "água", "agua",
            "rana", "rane", "rospo", "rospi", "anfibio", "anfibi", "fiume", "acqua",
        },
        boost_columns={
            "taxon_class": ["amphibia"],
            "source_queries": ["amphibians"],
            "search_document": ["rana", "anfibio", "frog", "agua", "жаба", "sapo", "rã", "rospo"],
        },
        boost_value=0.16,
    ),
    SearchIntent(
        name="raptor",
        terms={
            "rapaz", "rapaces", "aguila", "águila", "eagle", "hawk", "halcon", "halcón", "montaña",
            "орел", "орёл", "ястреб", "сокол", "хищная", "гора",
            "орел", "яструб", "сокіл", "хижий", "гора",
            "águia", "aguia", "falcão", "falcao", "ave de rapina", "montanha",
            "aquila", "falco", "rapace", "rapaci", "montagna",
        },
        boost_columns={
            "family": ["accipitridae"],
            "source_queries": ["raptors_accipitridae"],
            "search_document": ["ave rapaz", "eagle", "aguila", "águila", "montaña", "орел", "águia", "aquila"],
        },
        boost_value=0.16,
    ),
    SearchIntent(
        name="plant",
        terms={
            "planta", "plantas", "flor", "flores", "vegetal", "flower", "flowers", "plant",
            "растение", "растения", "цветок", "цветы",
            "рослина", "рослини", "квітка", "квіти",
            "planta", "plantas", "flor", "flores",
            "pianta", "piante", "fiore", "fiori",
        },
        boost_columns={
            "kingdom": ["plantae"],
            "taxon_class": ["magnoliopsida", "liliopsida"],
            "source_queries": ["flowering_plants"],
            "search_document": ["planta", "flor", "flowering", "рослина", "квітка", "planta", "fiore"],
        },
        boost_value=0.12,
    ),
    SearchIntent(
        name="mammal",
        terms={
            "mamifero", "mamífero", "mamiferos", "mamíferos", "mammal", "mammals",
            "млекопитающее", "млекопитающие", "ссавець", "ссавці",
            "mamífero", "mamifero", "mamíferos", "mammifero", "mammiferi",
        },
        boost_columns={
            "taxon_class": ["mammalia"],
            "source_queries": ["mammals"],
            "search_document": ["mamifero", "mamífero", "mammal", "ссавець", "mammifero"],
        },
        boost_value=0.08,
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
        boost_value=0.07,
    ),
]


SYNONYM_GROUPS = {
    # General
    "animal": "animalia animales fauna organismo especie",
    "animales": "animal animalia fauna organismo especie",
    "тварина": "animal animalia fauna organismo especie",
    "тварини": "animal animalia fauna organismo especie",
    "животное": "animal animalia fauna organismo especie",
    "животные": "animal animalia fauna organismo especie",
    "bicho": "insecto insecta animal pequeño alas",
    "bichos": "insectos insecta animales pequeños alas",
    "комаха": "insecto insecta insect bicho",
    "комахи": "insectos insecta insects bichos",
    "насекомое": "insecto insecta insect bicho",
    "насекомые": "insectos insecta insects bichos",
    "inseto": "insecto insecta insect bicho",
    "insetos": "insectos insecta insects bichos",
    "insetto": "insecto insecta insect bicho",
    "insetti": "insectos insecta insects bichos",

    # Birds
    "pajaro": "pájaro ave aves bird birds alas plumas",
    "pájaro": "pajaro ave aves bird birds alas plumas",
    "pajaros": "pájaros ave aves bird birds alas plumas",
    "pájaros": "pajaros ave aves bird birds alas plumas",
    "ave": "aves pajaro bird alas plumas",
    "aves": "ave pajaros birds alas plumas",
    "bird": "ave pajaro aves",
    "birds": "aves pajaros",
    "птица": "ave bird aves pajaro alas plumas",
    "птицы": "aves birds pajaros alas plumas",
    "птах": "ave bird aves pajaro alas plumas",
    "птахи": "aves birds pajaros alas plumas",
    "passaro": "pássaro ave bird pajaro",
    "pássaro": "passaro ave bird pajaro",
    "passaros": "pássaros aves birds pajaros",
    "pássaros": "passaros aves birds pajaros",
    "uccello": "ave bird pajaro",
    "uccelli": "aves birds pajaros",

    # Pink / flamingo
    "rosa": "rosado pink flamenco flamingo phoenicopterus roseus рожевий розовый",
    "rosado": "rosa pink flamenco flamingo phoenicopterus roseus",
    "pink": "rosa rosado flamenco flamingo phoenicopterus roseus",
    "flamenco": "flamingo phoenicopterus roseus pajaro rosa ave rosa humedal",
    "flamingo": "flamenco phoenicopterus roseus pink bird",
    "розовая": "rosa pink flamenco flamingo ave pajaro",
    "розовый": "rosa pink flamenco flamingo ave pajaro",
    "рожевий": "rosa pink flamenco flamingo ave pajaro",
    "рожева": "rosa pink flamenco flamingo ave pajaro",
    "uccello": "ave bird pajaro",
    "pássaro": "ave bird pajaro",

    # Polar bear
    "polar": "arctic artico ártico hielo ice nieve snow ursus maritimus oso polar polar bear urso orso ведмідь медведь",
    "hielo": "ice polar arctic artico ártico nieve snow ursus maritimus oso polar",
    "ice": "hielo polar arctic ursus maritimus polar bear",
    "oso": "ursus bear mammalia oso polar polar bear",
    "bear": "oso ursus mammalia polar bear",
    "ursus": "ursus maritimus oso polar polar bear",
    "медведь": "oso bear ursus mammalia polar bear",
    "медведи": "osos bears ursus mammalia",
    "белый": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "полярный": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "арктический": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "ведмідь": "oso bear ursus mammalia polar bear",
    "ведмеді": "osos bears ursus mammalia",
    "білий": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "полярний": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "арктичний": "polar hielo ice arctic ursus maritimus oso polar polar bear",
    "urso": "oso bear ursus mammalia polar bear",
    "ursos": "osos bears ursus mammalia",
    "gelo": "hielo ice polar arctic ursus maritimus",
    "orso": "oso bear ursus mammalia polar bear",
    "orsi": "osos bears ursus mammalia",
    "ghiaccio": "hielo ice polar arctic ursus maritimus",

    # Butterflies / moths
    "mariposa": "mariposas lepidoptera insecta butterfly butterflies polilla moth alas colores метелик borboleta farfalla",
    "mariposas": "mariposa lepidoptera insecta butterfly butterflies polillas moths alas colores метелики borboletas farfalle",
    "butterfly": "mariposa mariposas lepidoptera insecta butterflies",
    "butterflies": "mariposas mariposa lepidoptera insecta butterfly",
    "polilla": "polillas moth moths lepidoptera insecta mariposa",
    "polillas": "polilla moth moths lepidoptera insecta mariposas",
    "moth": "polilla lepidoptera insecta mariposa",
    "moths": "polillas lepidoptera insecta mariposas",
    "lepidoptera": "mariposa mariposas butterfly butterflies polilla moth insecta",
    "бабочка": "mariposa butterfly lepidoptera insecta alas",
    "бабочки": "mariposas butterflies lepidoptera insecta alas",
    "мотылек": "moth polilla lepidoptera insecta",
    "мотыльки": "moths polillas lepidoptera insecta",
    "метелик": "mariposa butterfly lepidoptera insecta alas",
    "метелики": "mariposas butterflies lepidoptera insecta alas",
    "міль": "moth polilla lepidoptera insecta",
    "borboleta": "mariposa butterfly lepidoptera insecta alas",
    "borboletas": "mariposas butterflies lepidoptera insecta alas",
    "farfalla": "mariposa butterfly lepidoptera insecta alas",
    "farfalle": "mariposas butterflies lepidoptera insecta alas",
    "falena": "moth polilla lepidoptera insecta",
    "falene": "moths polillas lepidoptera insecta",

    # Amphibians / frogs
    "rana": "ranas anfibio anfibios amphibia frog frogs agua rio río charca жаба rã sapo rospo",
    "ranas": "rana anfibio anfibios amphibia frog frogs agua rio río charca",
    "anfibio": "anfibios amphibia rana frog agua",
    "anfibios": "anfibio amphibia ranas frogs agua",
    "frog": "rana amphibia anfibio agua",
    "frogs": "ranas amphibia anfibios agua",
    "rio": "río agua dulce rana anfibio amphibia",
    "río": "rio agua dulce rana anfibio amphibia",
    "agua": "rio río humedal rana pez anfibio",
    "лягушка": "rana frog amphibia anfibio agua rio",
    "лягушки": "ranas frogs amphibia anfibios agua rio",
    "жаба": "rana frog amphibia anfibio agua rio sapo rospo",
    "жабы": "ranas frogs amphibia anfibios agua rio",
    "річка": "rio río agua rana frog amphibia",
    "река": "rio río agua rana frog amphibia",
    "sapo": "rana frog amphibia anfibio agua",
    "sapos": "ranas frogs amphibia anfibios agua",
    "rã": "rana frog amphibia anfibio agua",
    "rãs": "ranas frogs amphibia anfibios agua",
    "rospo": "rana frog amphibia anfibio agua",
    "rospi": "ranas frogs amphibia anfibios agua",
    "fiume": "rio río agua rana frog amphibia",
    "acqua": "agua rio rana frog amphibia",

    # Raptors
    "rapaz": "rapaces ave rapaz aguila águila eagle hawk halcon halcón accipitridae montaña",
    "rapaces": "rapaz aves rapaces aguilas eagles hawks accipitridae",
    "aguila": "águila eagle ave rapaz accipitridae aquila montaña",
    "águila": "aguila eagle ave rapaz accipitridae aquila montaña",
    "eagle": "aguila águila ave rapaz accipitridae",
    "hawk": "halcon halcón ave rapaz accipitridae",
    "montana": "montaña mountain ave rapaz aguila",
    "montaña": "montana mountain ave rapaz aguila",
    "орел": "aguila eagle ave rapaz accipitridae",
    "орёл": "aguila eagle ave rapaz accipitridae",
    "ястреб": "hawk ave rapaz accipitridae",
    "сокол": "falcon halcon ave rapaz",
    "орел": "aguila eagle ave rapaz accipitridae",
    "яструб": "hawk ave rapaz accipitridae",
    "сокіл": "falcon halcon ave rapaz",
    "águia": "aguila eagle ave rapaz accipitridae",
    "aguia": "aguila eagle ave rapaz accipitridae",
    "falcão": "falcon halcon ave rapaz",
    "falcao": "falcon halcon ave rapaz",
    "aquila": "aguila eagle ave rapaz accipitridae",
    "falco": "falcon halcon ave rapaz",

    # Plants / flowers
    "planta": "plantas plantae vegetal flor flores flowering plant рослина pianta",
    "plantas": "planta plantae vegetal flor flores flowering plants рослини piante",
    "flor": "flores planta plantae magnoliopsida flowering flower квітка fiore",
    "flores": "flor planta plantae magnoliopsida flowering flowers квіти fiori",
    "flower": "flor planta flowering",
    "flowers": "flores plantas flowering",
    "растение": "planta plant plantae vegetal flor flower",
    "растения": "plantas plants plantae vegetal flores flowers",
    "цветок": "flor flower planta plantae",
    "цветы": "flores flowers plantas plantae",
    "рослина": "planta plant plantae vegetal flor flower",
    "рослини": "plantas plants plantae vegetal flores flowers",
    "квітка": "flor flower planta plantae",
    "квіти": "flores flowers plantas plantae",
    "pianta": "planta plant plantae vegetal flor flower",
    "piante": "plantas plants plantae vegetal flores flowers",
    "fiore": "flor flower planta plantae",
    "fiori": "flores flowers plantas plantae",

    # Mammals / fish
    "mamifero": "mamífero mammalia mammal mamiferos",
    "mamífero": "mamifero mammalia mammal mamiferos",
    "mamiferos": "mamíferos mammalia mammals",
    "mamíferos": "mamiferos mammalia mammals",
    "mammal": "mamifero mammalia",
    "mammals": "mamiferos mammalia",
    "млекопитающее": "mamifero mammalia mammal",
    "млекопитающие": "mamiferos mammalia mammals",
    "ссавець": "mamifero mammalia mammal",
    "ссавці": "mamiferos mammalia mammals",
    "mammifero": "mamifero mammalia mammal",
    "mammiferi": "mamiferos mammalia mammals",
    "pez": "peces fish actinopterygii agua acuatico",
    "peces": "pez fish actinopterygii agua acuatico",
    "fish": "pez peces actinopterygii agua",
    "рыба": "pez fish actinopterygii agua",
    "риба": "pez fish actinopterygii agua",
    "peixe": "pez fish actinopterygii agua",
    "pesce": "pez fish actinopterygii agua",
}


def normalize_text(text: str) -> str:
    """
    Normaliza texto para búsqueda.

    Se conservan letras cirílicas para poder buscar en ruso/ucraniano.
    """
    normalized = unicodedata.normalize("NFKD", str(text).lower())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-zа-яёіїєґ0-9ñ\s]", " ", without_accents).strip()


def expand_query(query_text: str) -> str:
    """Expande la consulta con sinónimos multilingües e intenciones."""
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
    - sinónimos multilingües;
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
