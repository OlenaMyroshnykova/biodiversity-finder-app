"""Controlled Spanish/English query expansion for generic fallback search.

Concrete species names are intentionally not included here. Exact/common-name
matching is handled by the search document itself, not by hardcoded animal hacks.
"""
from __future__ import annotations

from src.search_components.normalizer import normalize_text

GENERIC_CATEGORY_SYNONYMS = {
    "animal": "animalia fauna especie organismo",
    "animales": "animalia fauna especies organismos",
    "plant": "plantae flora vegetal",
    "plants": "plantae flora vegetales",
    "planta": "plantae flora vegetal",
    "plantas": "plantae flora vegetales",
    "bird": "aves ave pajaro pájaro",
    "birds": "aves pajaros pájaros",
    "ave": "aves bird pajaro pájaro",
    "aves": "aves birds pajaros pájaros",
    "mammal": "mammalia mamifero mamífero",
    "mamifero": "mammalia mamífero mammal",
    "mamífero": "mammalia mamifero mammal",
    "insect": "insecta insecto",
    "insects": "insecta insectos",
    "insecto": "insecta insect",
    "insectos": "insecta insects",
    "flower": "flor flowering plantae",
    "flowers": "flores flowering plantae",
    "flor": "flower flowering plantae",
    "flores": "flowers flowering plantae",
    "water": "agua aquatic acuatico acuático",
    "agua": "water aquatic acuatico acuático",
    "aquatic": "agua acuatico acuático water",
    "acuatico": "aquatic water agua",
    "acuático": "aquatic water agua",
    "reptile": "reptilia reptil",
    "reptiles": "reptilia reptiles",
    "reptil": "reptilia reptile",
    "fish": "actinopterygii pez peces aquatic",
    "fishes": "actinopterygii peces aquatic",
    "pez": "actinopterygii fish aquatic",
    "peces": "actinopterygii fishes aquatic",
    "spider": "arachnida araneae araña",
    "spiders": "arachnida araneae arañas",
    "araña": "arachnida araneae spider",
    "arañas": "arachnida araneae spiders",
    "frog": "amphibia anura rana anfibio",
    "frogs": "amphibia anura ranas anfibios",
    "rana": "amphibia anura frog anfibio",
    "ranas": "amphibia anura frogs anfibios",
}


def expand_query(query_text: str) -> str:
    """Expand a query with a small controlled vocabulary."""
    normalized_query = normalize_text(query_text)
    words = normalized_query.split()
    expansions = [normalized_query]
    for word in words:
        synonym_text = GENERIC_CATEGORY_SYNONYMS.get(word)
        if synonym_text:
            expansions.append(synonym_text)
    return " ".join(expansions)
