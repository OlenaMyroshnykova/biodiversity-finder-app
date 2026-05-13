"""Expansión genérica de consultas.

Solo español e inglés. No se expanden ruso, ucraniano, portugués ni italiano
porque la UI ya no promete soporte multilingüe amplio.
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
    "ave": "aves bird pajaro pájaro",
    "aves": "aves birds pajaros pájaros",
    "bird": "aves ave pajaro pájaro",
    "birds": "aves pajaros pájaros",
    "mamifero": "mammalia mamífero mammal",
    "mamífero": "mammalia mamifero mammal",
    "mammal": "mammalia mamifero mamífero",
    "insecto": "insecta insect",
    "insect": "insecta insecto",
    "flor": "flower flowering plantae",
    "flower": "flor flowering plantae",
    "agua": "water aquatic acuatico acuático",
    "water": "agua aquatic acuatico acuático",
}


def expand_query(query_text: str) -> str:
    """Expande una consulta solo con categorías generales ES/EN."""
    normalized_query = normalize_text(query_text)
    words = normalized_query.split()
    expansions = [normalized_query]

    for word in words:
        synonym_text = GENERIC_CATEGORY_SYNONYMS.get(word)
        if synonym_text:
            expansions.append(synonym_text)

    return " ".join(expansions)
