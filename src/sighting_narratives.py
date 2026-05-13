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

_HABITAT_PHRASE = {
    "polar": "entornos polares",
    "wetland": "humedales, ríos y zonas costeras",
    "forest": "bosques y selvas",
    "desert": "desiertos y zonas semiáridas",
    "ocean": "ecosistemas oceánicos",
    "marine": "ecosistemas marinos",
    "savanna": "sabanas y praderas",
    "grassland": "praderas abiertas",
    "mountain": "montañas y altiplanos",
    "meadow": "praderas y jardines",
    "terrestrial": "entornos terrestres variados",
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


def build_sighting_narrative(row: pd.Series) -> str:
    """Genera una ficha narrativa basada únicamente en columnas del DataFrame."""
    scientific_name = str(row.get("scientific_name", "esta especie"))
    common_names = str(row.get("vernacular_names", "") or "").strip()
    taxon_class = str(row.get("taxon_class", "") or "")
    family = str(row.get("family", "familia desconocida"))
    habitat_tag = str(row.get("habitat_tag", "") or "")
    size_tag = str(row.get("size_tag", "") or "")
    color_tag = str(row.get("color_tag", "") or "")
    observations = int(row.get("observations", 0) or 0)
    countries_raw = str(row.get("countries", "") or "")
    conservation_status = str(row.get("iucn_category", row.get("conservation_status", "NO_DATA")) or "NO_DATA").upper().strip()
    conservation_source = str(row.get("iucn_source", row.get("conservation_source", "No IUCN data")) or "No IUCN data")

    public_name = scientific_name
    if common_names:
        first_name = common_names.split("|")[0].strip()
        if first_name:
            public_name = first_name

    organism_type = _CLASS_INTRO.get(taxon_class, taxon_class.lower() if taxon_class else "especie")

    habitat_phrase = "diversos ecosistemas"
    for key, phrase in _HABITAT_PHRASE.items():
        if key in habitat_tag.lower():
            habitat_phrase = phrase
            break

    color_sentence = ""
    if color_tag and "unknown" not in color_tag:
        color_sentence = f" Su coloración aparece descrita con etiquetas como **{color_tag.split()[0]}**."

    if size_tag and "unknown" not in size_tag:
        if "large" in size_tag or "grande" in size_tag:
            size_sentence = "de tamaño grande"
        elif "small" in size_tag or "pequeño" in size_tag or "tiny" in size_tag:
            size_sentence = "de tamaño pequeño"
        else:
            size_sentence = "de tamaño medio"
    else:
        size_sentence = "con tamaño no especificado"

    country_list = [country.strip() for country in countries_raw.split(",") if country.strip()]
    if len(country_list) > 3:
        countries_description = f"{', '.join(country_list[:3])} y otros {len(country_list) - 3} países"
    elif country_list:
        countries_description = ", ".join(country_list)
    else:
        countries_description = "diversas regiones"

    if observations >= 1000:
        observations_description = f"más de {observations:,} observaciones registradas"
    elif observations > 0:
        observations_description = f"{observations} observaciones en el dataset"
    else:
        observations_description = "observaciones escasas en el dataset"

    conservation_phrase = _CONSERVATION_PHRASE.get(
        conservation_status,
        "con estado de conservación pendiente de evaluación",
    )

    return (
        f"**{public_name}** (*{scientific_name}*) es un {organism_type} de la familia **{family}**, "
        f"asociado a {habitat_phrase}. Es {size_sentence}.{color_sentence} "
        f"En el dataset cuenta con {observations_description} en {countries_description}. "
        f"Su estado de conservación figura como {conservation_phrase}. "
        f"Fuente de conservación: **{conservation_source}**."
    )
