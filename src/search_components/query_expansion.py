"""Expansión genérica de consultas.

Este módulo no contiene animales concretos. Solo añade palabras amplias
para que el usuario pueda buscar por categorías generales.
"""

from __future__ import annotations

from src.search_components.normalizer import normalize_text


GENERIC_CATEGORY_SYNONYMS = {
    # Español / English
    "animal": "animalia fauna especie organismo",
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

    # Русский / Українська
    "животное": "animal animalia fauna",
    "животные": "animal animalia fauna",
    "тварина": "animal animalia fauna",
    "тварини": "animal animalia fauna",
    "растение": "planta plantae flora",
    "растения": "planta plantae flora",
    "рослина": "planta plantae flora",
    "рослини": "planta plantae flora",
    "птица": "ave bird aves",
    "птицы": "ave bird aves",
    "птах": "ave bird aves",
    "птахи": "ave bird aves",
    "насекомое": "insecto insect insecta",
    "насекомые": "insecto insect insecta",
    "комаха": "insecto insect insecta",
    "комахи": "insecto insect insecta",

    # Português / Italiano
    "animalia": "animal fauna especie",
    "plantae": "planta plant flora",
    "pássaro": "ave bird aves",
    "passaro": "ave bird aves",
    "uccello": "ave bird aves",
    "inseto": "insecto insect insecta",
    "insetto": "insecto insect insecta",
    "fiore": "flor flower plantae",
}


def expand_query(query_text: str) -> str:
    """Expande una consulta solo con categorías generales."""
    normalized_query = normalize_text(query_text)
    words = normalized_query.split()
    expansions = [normalized_query]

    for word in words:
        synonym_text = GENERIC_CATEGORY_SYNONYMS.get(word)

        if synonym_text:
            expansions.append(synonym_text)

    return " ".join(expansions)
