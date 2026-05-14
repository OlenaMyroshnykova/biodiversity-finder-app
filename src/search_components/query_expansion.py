"""Expansión genérica de consultas.

Este módulo NO contiene hacks por especie. Las especies concretas deben aparecer
por sus nombres comunes en `vernacular_names` y `search_document`, generados en
training. Aquí solo viven conceptos generales ES/EN usados en frases humanas.
"""
from __future__ import annotations

from src.search_components.normalizer import normalize_text

GENERIC_QUERY_SYNONYMS: dict[str, str] = {
    "animal": "animalia fauna especie organismo",
    "animales": "animalia fauna especies organismos",
    "bicho": "animalia fauna insecto pequeno pequeño",
    "bichos": "animalia fauna insectos pequenos pequeños",
    "planta": "plantae flora vegetal",
    "plantas": "plantae flora vegetales",
    "plant": "plantae flora vegetal",
    "plants": "plantae flora vegetales",
    "ave": "aves bird pajaro pájaro plumas",
    "aves": "aves birds pajaros pájaros plumas",
    "bird": "aves ave pajaro pájaro feathers",
    "birds": "aves pajaros pájaros feathers",
    "mamifero": "mammalia mammal mamifero",
    "mamífero": "mammalia mammal mamifero",
    "mammal": "mammalia mamifero mamífero",
    "insecto": "insecta insect bicho pequeno pequeño",
    "insect": "insecta insecto bug small",
    "reptil": "reptilia reptile escamas",
    "reptile": "reptilia reptil scales",
    "anfibio": "amphibia amphibian humedal agua",
    "amphibian": "amphibia anfibio wetland water",
    "pez": "actinopterygii chondrichthyes fish agua mar rio río",
    "fish": "actinopterygii chondrichthyes pez water sea river",
    "flor": "flower flowering plantae colorido",
    "flower": "flor flowering plantae colorful",
    "desierto": "desert arid arido árido",
    "desert": "desierto arid arido árido",
    "bosque": "forest woodland",
    "forest": "bosque woodland",
    "agua": "water aquatic acuatico acuático humedal rio río lago",
    "water": "agua aquatic acuatico acuático wetland river lake",
    "rosa": "pink rosado",
    "pink": "rosa rosado",
    "azul": "blue",
    "blue": "azul",
    "verde": "green",
    "green": "verde",
    "pequeno": "small tiny little pequeño",
    "pequeño": "small tiny little pequeno",
    "small": "pequeno pequeño tiny little",
    "grande": "large big gigante",
    "large": "grande big gigante",
}


def expand_query(query_text: str) -> str:
    """Expande solo vocabulario conceptual, no especies concretas."""
    normalized_query = normalize_text(query_text)
    expansions = [normalized_query]
    for word in normalized_query.split():
        expansion = GENERIC_QUERY_SYNONYMS.get(word)
        if expansion:
            expansions.append(expansion)
    return " ".join(part for part in expansions if part).strip()
