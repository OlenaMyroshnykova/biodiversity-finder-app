"""Generic query expansion for broad ES/EN categories.

This dictionary must not contain concrete species or demo animals. Exact common
names are handled by the fallback text search over ``vernacular_names`` and
``search_document``.
"""
from __future__ import annotations

from src.search_components.normalizer import normalize_text

GENERIC_CATEGORY_SYNONYMS = {
    "animal": "animalia fauna especie organismo",
    "animals": "animalia fauna especies organismos",
    "animales": "animalia fauna especies organismos",
    "planta": "plantae flora vegetal",
    "plantas": "plantae flora vegetales",
    "plant": "plantae flora vegetal",
    "plants": "plantae flora vegetales",
    "ave": "aves bird pajaro pajaro",
    "aves": "aves birds pajaros pajaros",
    "bird": "aves ave pajaro pajaro",
    "birds": "aves pajaros pajaros",
    "mamifero": "mammalia mamifero mammal",
    "mamífero": "mammalia mamifero mammal",
    "mammal": "mammalia mamifero mamifero",
    "insecto": "insecta insect",
    "insect": "insecta insecto",
    "flor": "flower flowering plantae",
    "flower": "flor flowering plantae",
    "agua": "water aquatic acuatico acuatico",
    "water": "agua aquatic acuatico acuatico",
    "desierto": "desert seco arido arido",
    "desert": "desierto dry arid",
    "sabana": "savanna grassland pradera",
    "savanna": "sabana grassland pradera",
    "bosque": "forest woodland",
    "forest": "bosque woodland",
}


def expand_query(query_text: str) -> str:
    """Expand a query only with broad category terms."""
    normalized_query = normalize_text(query_text)
    words = normalized_query.split()
    expansions = [normalized_query]
    for word in words:
        synonym_text = GENERIC_CATEGORY_SYNONYMS.get(word)
        if synonym_text:
            expansions.append(synonym_text)
    return " ".join(expansions)
