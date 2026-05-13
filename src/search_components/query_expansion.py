"""Small Spanish/English query expansion for fallback name search.

The main vibe-search uses structured filters before TF-IDF. This expansion is
only for fallback searches by name/taxonomy and intentionally avoids Russian,
Ukrainian, Portuguese or Italian terms so the UI does not promise unstable
multi-language behavior.
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
    "insecto": "insecta insect",
    "flower": "flor flowering plantae",
    "flor": "flower flowering plantae",
    "water": "agua aquatic acuatico acuático",
    "agua": "water aquatic acuatico acuático",
    "crocodile": "crocodylia crocodilian reptilia cocodrilo caiman",
    "crocodiles": "crocodylia crocodilian reptilia",
    "cocodrilo": "crocodylia crocodile crocodilian reptilia caiman",
    "cocodrilos": "crocodylia crocodiles reptilia",
    "snake": "serpentes reptilia serpiente vibora",
    "snakes": "serpentes reptilia serpientes",
    "serpiente": "serpentes snake reptilia vibora",
    "serpientes": "serpentes snakes reptilia",
    "shark": "chondrichthyes selachimorpha tiburon",
    "tiburon": "chondrichthyes shark selachimorpha",
    "tiburón": "chondrichthyes shark selachimorpha",
    "fish": "actinopterygii pisces pez teleostei",
    "pez": "actinopterygii fish pisces teleostei",
    "spider": "arachnida araneae araña",
    "araña": "arachnida araneae spider",
    "mushroom": "fungi basidiomycota hongo seta",
    "hongo": "fungi basidiomycota mushroom seta",
    "frog": "amphibia anura rana anfibio",
    "rana": "amphibia anura frog anfibio",
    "butterfly": "lepidoptera insecta mariposa",
    "mariposa": "lepidoptera insecta butterfly",
    "lion": "panthera leo felidae leon león",
    "leon": "panthera leo felidae lion",
    "león": "panthera leo felidae lion",
    "jaguar": "panthera onca felidae",
    "flamingo": "phoenicopteriformes phoenicopteridae flamenco",
    "flamenco": "phoenicopteriformes phoenicopteridae flamingo",
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
