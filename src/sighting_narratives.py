"""Generador de fichas narrativas tipo National Geographic."""

from __future__ import annotations

import pandas as pd

_CLASS_INTRO = {
    "Mammalia": "mamífero",
    "Aves": "ave",
    "Reptilia": "reptil",
    "Amphibia": "anfibio",
    "Actinopterygii": "pez óseo",
    "Chondrichthyes": "condrictio",
    "Insecta": "insecto",
    "Arachnida": "arácnido",
    "Magnoliopsida": "planta con flor",
    "Fungi": "hongo",
}

_CONSERVATION_PHRASE = {
    "LC": "clasificada como especie de Preocupación Menor",
    "NT": "considerada Casi Amenazada, lo que requiere seguimiento",
    "VU": "declarada Vulnerable",
    "EN": "catalogada En Peligro",
    "CR": "en Peligro Crítico",
    "EW": "extinta en estado salvaje",
    "EX": "extinta",
    "DD": "con Datos Insuficientes",
    "NE": "aún no evaluada",
    "NO_DATA": "sin datos IUCN disponibles en esta ejecución",
}

_SIZE_PHRASES = [
    ("large", "de tamaño grande"),
    ("grande", "de tamaño grande"),
    ("small", "de tamaño pequeño"),
    ("pequeño", "de tamaño pequeño"),
    ("pequeno", "de tamaño pequeño"),
    ("tiny", "de tamaño muy pequeño"),
    ("medium", "de tamaño medio"),
    ("mediano", "de tamaño medio"),
]

_COLOR_LABELS = [
    ("brown", "marrón"),
    ("marron", "marrón"),
    ("white", "blanco"),
    ("black", "negro"),
    ("red", "rojo"),
    ("pink", "rosa"),
    ("blue", "azul"),
    ("green", "verde"),
    ("yellow", "amarillo"),
    ("colorful", "colorido"),
]


def build_sighting_narrative(row: pd.Series) -> str:
    """Genera una ficha narrativa basada únicamente en columnas del DataFrame.

    Important: ``habitat_tag``, ``size_tag`` and ``color_tag`` are search
    signals generated for the educational vibe-search. They are not official
    ecological descriptions. The narrative must therefore avoid strong phrases
    like "associated with forests" when the artifact contains mixed or noisy
    search tags.
    """
    scientific_name = str(row.get("scientific_name", "esta especie"))
    common_names = str(row.get("vernacular_names", "") or "").strip()
    taxon_class = str(row.get("taxon_class", "") or "")
    family = str(row.get("family", "familia desconocida"))
    size_tag = str(row.get("size_tag", "") or "")
    color_tag = str(row.get("color_tag", "") or "")
    observations = safe_int(row.get("observations", 0))
    countries_raw = str(row.get("countries", "") or "")
    conservation_status = str(
        row.get("iucn_category", row.get("conservation_status", "NO_DATA")) or "NO_DATA"
    ).upper().strip()
    conservation_source = str(
        row.get("iucn_source", row.get("conservation_source", "No IUCN data"))
        or "No IUCN data"
    )

    public_name = scientific_name
    if common_names:
        first_name = common_names.split("|")[0].strip()
        if first_name:
            public_name = first_name

    organism_type = _CLASS_INTRO.get(
        taxon_class,
        taxon_class.lower() if taxon_class else "especie",
    )
    size_sentence = build_size_sentence(size_tag)
    color_sentence = build_color_sentence(color_tag)
    countries_description = build_countries_description(countries_raw)
    observations_description = build_observations_description(observations)
    conservation_phrase = _CONSERVATION_PHRASE.get(
        conservation_status,
        "con estado de conservación pendiente de evaluación",
    )

    return (
        f"**{public_name}** (*{scientific_name}*) es un {organism_type} de la familia "
        f"**{family}**. En esta enciclopedia se describe {size_sentence}."
        f"{color_sentence} "
        f"El artifact registra {observations_description} en {countries_description}. "
        "Las señales de hábitat se usan solo para orientar la búsqueda y deben "
        "leerse junto con el mapa de avistamientos. "
        f"Su estado de conservación figura como {conservation_phrase}. "
        f"Fuente de conservación: **{conservation_source}**."
    )


def safe_int(value: object) -> int:
    """Convert a dataframe value to int without breaking the card."""
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def build_size_sentence(size_tag: str) -> str:
    """Build a cautious size sentence from search tags."""
    normalized = str(size_tag or "").lower()
    if not normalized or normalized in {"unknown", "nan", "none", "no_data"}:
        return "con tamaño no especificado"

    for token, phrase in _SIZE_PHRASES:
        if token in normalized:
            return phrase
    return "con tamaño aproximado no clasificado"


def build_color_sentence(color_tag: str) -> str:
    """Build a cautious color sentence from search tags."""
    normalized = str(color_tag or "").lower()
    if not normalized or normalized in {"unknown", "nan", "none", "no_data"}:
        return ""

    for token, label in _COLOR_LABELS:
        if token in normalized:
            return f" Su color aparece como señal educativa de búsqueda: **{label}**."
    return ""


def build_countries_description(countries_raw: str) -> str:
    """Summarize countries without overloading the card."""
    country_list = [country.strip() for country in str(countries_raw or "").split(",") if country.strip()]
    if len(country_list) > 3:
        return f"{', '.join(country_list[:3])} y otros {len(country_list) - 3} países"
    if country_list:
        return ", ".join(country_list)
    return "diversas regiones"


def build_observations_description(observations: int) -> str:
    """Summarize observation count."""
    if observations >= 1000:
        return f"más de {observations:,} observaciones"
    if observations > 0:
        return f"{observations} observaciones"
    return "observaciones escasas"
