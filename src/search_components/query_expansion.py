"""Query expansion for fallback name search.

This module keeps two concepts separate:
- ``GENERIC_CATEGORY_SYNONYMS``: broad categories only. Tests use this dictionary
  to ensure we do not hide species-specific hacks inside generic vocabulary.
- ``EXACT_NAME_SYNONYMS``: small ES/EN helper aliases for common-name fallback.

Structured vibe-search still lives in ``natural_language_query.py`` and uses
``df.loc`` over size/habitat/color/group tags. This file only improves fallback
search when the user writes a concrete common name such as ``lion`` or
``cocodrilo``.
"""
from __future__ import annotations

from src.search_components.normalizer import normalize_text

GENERIC_CATEGORY_SYNONYMS: dict[str, str] = {
    # Project scope: Spanish + English only for demo promises.
    "animal": "animalia fauna especie organismo",
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
    "reptil": "reptilia reptile escamas",
    "reptiles": "reptilia reptiles escamas",
    "anfibio": "amphibia amphibian",
    "amphibian": "amphibia anfibio",
    "pez": "actinopterygii fish",
    "peces": "actinopterygii fish",
    "fish": "actinopterygii pez peces",
    "flor": "flower flowering plantae",
    "flower": "flor flowering plantae",
    "agua": "water aquatic acuatico acuatico",
    "water": "agua aquatic acuatico acuatico",
}

# Concrete-name fallback aliases. This is intentionally NOT the generic synonym
# dictionary, so tests can verify that generic categories remain generic.
EXACT_NAME_SYNONYMS: dict[str, str] = {
    "lion": "panthera leo leon",
    "leon": "panthera leo lion",
    "león": "panthera leo lion",
    "cocodrilo": "crocodylia crocodylus crocodile reptilia caiman",
    "cocodrilos": "crocodylia crocodiles reptilia",
    "crocodile": "crocodylia crocodylus cocodrilo reptilia caiman",
    "crocodiles": "crocodylia crocodiles reptilia",
    "caiman": "crocodylia crocodilian reptilia",
    "caimán": "crocodylia crocodilian reptilia",
    "shark": "chondrichthyes selachimorpha tiburon",
    "tiburon": "chondrichthyes selachimorpha shark",
    "tiburón": "chondrichthyes selachimorpha shark",
    "snake": "serpentes reptilia serpiente",
    "serpiente": "serpentes reptilia snake",
    "lizard": "reptilia lacertilia lagarto",
    "lagarto": "reptilia lacertilia lizard",
    "spider": "arachnida araneae arana",
    "araña": "arachnida araneae spider",
    "arana": "arachnida araneae spider",
    "eagle": "accipitridae aves rapaz aguila",
    "aguila": "accipitridae aves rapaz eagle",
    "águila": "accipitridae aves rapaz eagle",
    "frog": "amphibia anura rana anfibio",
    "rana": "amphibia anura frog amphibian",
}


def expand_query(query_text: str) -> str:
    """Expand a user query for fallback TF-IDF/name search.

    The expansion is intentionally ES/EN only. Cyrillic or other-language common
    names are still searchable when they already exist in ``vernacular_names``;
    we simply do not advertise or inject those languages as demo vocabulary.
    """
    normalized_query = normalize_text(query_text)
    words = normalized_query.split()
    expansions = [normalized_query]

    for word in words:
        generic_text = GENERIC_CATEGORY_SYNONYMS.get(word)
        if generic_text:
            expansions.append(generic_text)

        exact_text = EXACT_NAME_SYNONYMS.get(word)
        if exact_text:
            expansions.append(exact_text)

    return " ".join(part for part in expansions if part).strip()
