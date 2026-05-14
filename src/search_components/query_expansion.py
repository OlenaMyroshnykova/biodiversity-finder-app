"""Query expansion for generic fallback search.

Architecture note:
- Generic categories stay broad: animal, plant, bird, mammal, water, etc.
- The app must not hide one-off species hacks in generic vocabulary.
- Concrete common names can still have small ES/EN aliases as fallback, while
  the real source of truth remains the artifact search_document built by the
  training pipeline.
"""
from __future__ import annotations

from src.search_components.normalizer import normalize_text


GENERIC_CATEGORY_SYNONYMS: dict[str, str] = {
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
    """Expand a user query for fallback TF-IDF/name search."""
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
