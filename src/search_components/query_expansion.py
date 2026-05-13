"""Expansión de consultas de búsqueda.

Traduce palabras del usuario (categorías generales y nombres concretos
de animales en español, inglés y ruso) a términos científicos para
mejorar la búsqueda TF-IDF sobre la enciclopedia.
"""

from __future__ import annotations

from src.search_components.normalizer import normalize_text


GENERIC_CATEGORY_SYNONYMS = {
    # ── Categorías generales — Español / English ─────────────────────────
    "animal":    "animalia fauna especie organismo",
    "animales":  "animalia fauna especies organismos",
    "planta":    "plantae flora vegetal",
    "plantas":   "plantae flora vegetales",
    "plant":     "plantae flora vegetal",
    "plants":    "plantae flora vegetales",
    "ave":       "aves bird pajaro pájaro",
    "aves":      "aves birds pajaros pájaros",
    "bird":      "aves ave pajaro pájaro",
    "birds":     "aves pajaros pájaros",
    "mamifero":  "mammalia mamífero mammal",
    "mamífero":  "mammalia mamifero mammal",
    "mammal":    "mammalia mamifero mamífero",
    "insecto":   "insecta insect",
    "insect":    "insecta insecto",
    "flor":      "flower flowering plantae",
    "flower":    "flor flowering plantae",
    "agua":      "water aquatic acuatico acuático",
    "water":     "agua aquatic acuatico acuático",

    # ── Русский / Українська ─────────────────────────────────────────────
    "животное":  "animal animalia fauna",
    "животные":  "animal animalia fauna",
    "тварина":   "animal animalia fauna",
    "тварини":   "animal animalia fauna",
    "растение":  "planta plantae flora",
    "растения":  "planta plantae flora",
    "рослина":   "planta plantae flora",
    "рослини":   "planta plantae flora",
    "птица":     "ave bird aves",
    "птицы":     "ave bird aves",
    "птах":      "ave bird aves",
    "птахи":     "ave bird aves",
    "насекомое": "insecto insect insecta",
    "насекомые": "insecto insect insecta",
    "комаха":    "insecto insect insecta",
    "комахи":    "insecto insect insecta",

    # ── Português / Italiano ─────────────────────────────────────────────
    "animalia":  "animal fauna especie",
    "plantae":   "planta plant flora",
    "pássaro":   "ave bird aves",
    "passaro":   "ave bird aves",
    "uccello":   "ave bird aves",
    "inseto":    "insecto insect insecta",
    "insetto":   "insecto insect insecta",
    "fiore":     "flor flower plantae",

    # ── Animales concretos — Español ─────────────────────────────────────
    "cocodrilo":  "crocodylia crocodile crocodilian reptilia caiman",
    "cocodrilos": "crocodylia crocodiles reptilia",
    "caimán":     "crocodylia crocodilian reptilia caiman",
    "caiman":     "crocodylia crocodilian reptilia caiman",
    "lagarto":    "reptilia lacertilia lizard iguana",
    "lagartija":  "reptilia lacertilia lizard",
    "serpiente":  "serpentes snake reptilia víbora",
    "serpientes": "serpentes snakes reptilia",
    "víbora":     "serpentes viperidae snake reptilia",
    "iguana":     "iguana reptilia lacertilia",
    "tiburon":    "chondrichthyes shark selachimorpha tiburon",
    "tiburón":    "chondrichthyes shark selachimorpha",
    "tiburones":  "chondrichthyes sharks selachimorpha",
    "raya":       "chondrichthyes ray batoidea",
    "rayas":      "chondrichthyes rays batoidea",
    "pez":        "actinopterygii fish pisces teleostei",
    "peces":      "actinopterygii fish pisces teleostei",
    "araña":      "arachnida araneae spider",
    "arañas":     "arachnida araneae spiders",
    "escorpion":  "arachnida scorpiones scorpion",
    "escorpión":  "arachnida scorpiones scorpion",
    "hongo":      "fungi basidiomycota ascomycota mushroom seta",
    "hongos":     "fungi basidiomycota mushrooms setas",
    "seta":       "fungi basidiomycota mushroom hongo",
    "setas":      "fungi basidiomycota mushrooms hongos",
    "oso":        "ursidae bear mammalia",
    "ballena":    "cetacea whale mammalia oceano",
    "delfin":     "cetacea dolphin mammalia",
    "delfín":     "cetacea dolphin mammalia",
    "reptil":     "reptilia reptile escamas",
    "reptiles":   "reptilia reptiles escamas",

    # ── Animales concretos — English ─────────────────────────────────────
    "crocodile":  "crocodylia crocodilian reptilia cocodrilo caiman",
    "crocodiles": "crocodylia crocodilian reptilia",
    "alligator":  "crocodylia crocodilian reptilia",
    "lizard":     "reptilia lacertilia lagarto iguana",
    "lizards":    "reptilia lacertilia lagartos",
    "snake":      "serpentes reptilia serpiente víbora",
    "snakes":     "serpentes reptilia serpientes",
    "shark":      "chondrichthyes selachimorpha tiburon",
    "sharks":     "chondrichthyes selachimorpha tiburones",
    "ray":        "chondrichthyes batoidea raya",
    "fish":       "actinopterygii pisces pez teleostei",
    "spider":     "arachnida araneae araña",
    "spiders":    "arachnida araneae arañas",
    "scorpion":   "arachnida scorpiones escorpion",
    "mushroom":   "fungi basidiomycota hongo seta",
    "mushrooms":  "fungi basidiomycota hongos setas",
    "bear":       "ursidae mammalia oso",
    "whale":      "cetacea mammalia ballena oceano",
    "dolphin":    "cetacea mammalia delfin oceano",
    "reptile":    "reptilia escamas lagarto serpiente",
    "reptiles":   "reptilia escamas",
    "frog":       "amphibia anura rana anfibio",
    "toad":       "amphibia anura sapo anfibio",
    "butterfly":  "lepidoptera insecta mariposa",
    "moth":       "lepidoptera insecta polilla",
    "eagle":      "accipitridae aves rapaz aguila",
    "hawk":       "accipitridae aves rapaz halcon",

    # ── Animales concretos — Русский ─────────────────────────────────────
    "крокодил":        "crocodylia crocodile reptilia cocodrilo",
    "крокодилы":       "crocodylia crocodiles reptilia",
    "аллигатор":       "crocodylia alligator reptilia",
    "кайман":          "crocodylia caiman reptilia",
    "ящерица":         "reptilia lacertilia lizard lagarto",
    "змея":            "serpentes snake reptilia serpiente",
    "змеи":            "serpentes snakes reptilia",
    "игуана":          "iguana reptilia lacertilia",
    "рептилия":        "reptilia reptile escamas",
    "рептилии":        "reptilia reptiles",
    "акула":           "chondrichthyes shark selachimorpha tiburon",
    "акулы":           "chondrichthyes sharks selachimorpha",
    "скат":            "chondrichthyes ray batoidea raya",
    "рыба":            "actinopterygii fish pisces pez",
    "рыбы":            "actinopterygii fish pisces peces",
    "паук":            "arachnida araneae spider araña",
    "пауки":           "arachnida araneae spiders",
    "скорпион":        "arachnida scorpiones scorpion escorpion",
    "гриб":            "fungi basidiomycota mushroom hongo",
    "грибы":           "fungi basidiomycota mushrooms hongos",
    "медведь":         "ursidae bear mammalia oso",
    "кит":             "cetacea whale mammalia ballena",
    "дельфин":         "cetacea dolphin mammalia delfin",
    "лягушка":         "amphibia anura frog rana",
    "жаба":            "amphibia anura toad sapo",
    "бабочка":         "lepidoptera insecta butterfly mariposa",
    "орёл":            "accipitridae aves eagle aguila",
    "орел":            "accipitridae aves eagle aguila",
}


def expand_query(query_text: str) -> str:
    """Expande una consulta con categorías generales y nombres concretos."""
    normalized_query = normalize_text(query_text)
    words = normalized_query.split()
    expansions = [normalized_query]

    for word in words:
        synonym_text = GENERIC_CATEGORY_SYNONYMS.get(word)
        if synonym_text:
            expansions.append(synonym_text)

    return " ".join(expansions)
