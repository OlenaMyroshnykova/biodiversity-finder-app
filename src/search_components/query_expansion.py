"""Query expansion helpers for fallback name search.

The structured vibe search remains Spanish + English. This module only expands
common-name fallback queries and keeps concrete species aliases out of the
generic category dictionary.
"""
from __future__ import annotations

import re
import unicodedata

# Generic terms only: groups, habitats, colors, sizes. No concrete species here.
GENERIC_CATEGORY_SYNONYMS: dict[str, str] = {
    "animal": "animalia fauna especie organismo",
    "animales": "animalia fauna especies organismos",
    "planta": "plantae flora vegetal",
    "plantas": "plantae flora vegetales",
    "ave": "aves bird birds pajaro pájaro plumas",
    "aves": "aves bird birds pajaros pájaros plumas",
    "mamifero": "mammalia mammal mammals mamífero mamíferos",
    "mamífero": "mammalia mammal mammals mamifero mamiferos",
    "reptil": "reptilia reptile reptiles",
    "anfibio": "amphibia amphibian amphibians",
    "insecto": "insecta insect insectos insects",
    "aracnido": "arachnida arachnid arachnids",
    "araña": "arachnida araneae spider",
    "pez": "actinopterygii fish fishes",
    "flor": "plantae flower flowers",
    "arbol": "plantae tree trees árbol",
    "árbol": "plantae tree trees arbol",
    "agua": "water aquatic acuatico acuático",
    "bosque": "forest woodland",
    "selva": "forest jungle rainforest",
    "desierto": "desert arid",
    "sabana": "savanna grassland",
    "montana": "mountain montaña alpine",
    "montaña": "mountain montana alpine",
    "humedal": "wetland swamp marsh",
    "mar": "ocean sea marine",
    "oceano": "ocean sea marine océano",
    "océano": "ocean sea marine oceano",
    "grande": "large big",
    "pequeno": "small tiny pequeño",
    "pequeño": "small tiny pequeno",
    "mediano": "medium",
    "rosa": "pink",
    "marron": "brown marrón",
    "marrón": "brown marron",
    "negro": "black",
    "blanco": "white",
    "verde": "green",
    "rojo": "red",
    "amarillo": "yellow",
    "azul": "blue",
}

# Specific common-name aliases belong here, not in GENERIC_CATEGORY_SYNONYMS.
# Spanish + English only for app promises, with a few scientific expansions for
# name fallback. This does not drive the structured vibe search.
SPECIFIC_NAME_ALIASES: dict[str, str] = {
    "lion": "panthera leo",
    "leon": "panthera leo león",
    "león": "panthera leo leon",
    "cocodrilo": "crocodylus crocodile",
    "crocodile": "crocodylus cocodrilo",
    "jaguar": "panthera onca",
    "leopard": "panthera pardus",
    "leopardo": "panthera pardus",
    "tiger": "panthera tigris",
}


def _normalize_for_matching(text: str) -> str:
    text = str(text or "").lower()
    decomposed = unicodedata.normalize("NFKD", text)
    text_without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return text_without_accents


def expand_query(query: str) -> str:
    """Expand a user query with controlled Spanish/English synonyms."""
    original = str(query or "").strip()
    normalized = _normalize_for_matching(original)
    tokens = set(re.findall(r"[\wáéíóúñü]+", original.lower(), flags=re.UNICODE))
    normalized_tokens = set(re.findall(r"[\w]+", normalized, flags=re.UNICODE))

    expansions: list[str] = [original]

    for key, value in GENERIC_CATEGORY_SYNONYMS.items():
        normalized_key = _normalize_for_matching(key)
        if key in tokens or normalized_key in normalized_tokens:
            expansions.append(value)

    for key, value in SPECIFIC_NAME_ALIASES.items():
        normalized_key = _normalize_for_matching(key)
        if key in tokens or normalized_key in normalized_tokens:
            expansions.append(value)

    return " ".join(part for part in expansions if part).strip()
