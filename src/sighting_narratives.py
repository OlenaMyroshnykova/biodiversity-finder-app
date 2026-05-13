"""Generador de fichas narrativas tipo National Geographic."""

from __future__ import annotations

import pandas as pd


# Vocabulario para narración enriquecida por clase taxonómica
_CLASS_INTRO = {
    "Mammalia":        "mamífero",
    "Aves":            "ave",
    "Reptilia":        "reptil",
    "Amphibia":        "anfibio",
    "Actinopterygii":  "pez óseo",
    "Chondrichthyes":  "condrictio (tiburón o raya)",
    "Insecta":         "insecto",
    "Arachnida":       "arácnido",
    "Magnoliopsida":   "planta con flor",
    "Fungi":           "hongo",
}

_HABITAT_PHRASE = {
    "polar":    "los gélidos entornos árticos",
    "wetland":  "humedales, ríos y zonas costeras",
    "forest":   "densos bosques y selvas",
    "desert":   "áridos desiertos y zonas semiáridas",
    "ocean":    "las profundidades del océano",
    "marine":   "ecosistemas marinos",
    "savanna":  "vastas sabanas y praderas",
    "mountain": "escarpadas montañas y altiplanos",
    "meadow":   "praderas y jardines",
    "terrestrial": "entornos terrestres variados",
}

_CONSERVATION_PHRASE = {
    "LC": "actualmente clasificada como especie de Preocupación Menor",
    "NT": "considerada Casi Amenazada, lo que requiere seguimiento",
    "VU": "declarada Vulnerable por la reducción de sus poblaciones",
    "EN": "catalogada En Peligro de extinción",
    "CR": "en Peligro Crítico, al borde de la extinción",
    "EW": "extinta en estado salvaje, solo sobrevive en cautividad",
    "EX": "extinta, sin individuos conocidos en la actualidad",
    "DD": "con Datos Insuficientes para evaluar su estado real",
    "NE": "aún no evaluada por organismos de conservación internacionales",
}


def build_sighting_narrative(row: pd.Series) -> str:
    """Genera una ficha narrativa estilo National Geographic a partir de los datos.

    Usa exclusivamente los datos del DataFrame: nombre científico, clase,
    familia, hábitat, tamaño, color, observaciones, países y conservación.
    No requiere llamadas a servicios externos.
    """
    scientific_name = str(row.get("scientific_name", "esta especie"))
    common_names    = str(row.get("vernacular_names", "") or "").strip()
    taxon_class     = str(row.get("taxon_class", "") or "")
    family          = str(row.get("family", "familia desconocida"))
    habitat_tag     = str(row.get("habitat_tag", "") or "")
    size_tag        = str(row.get("size_tag", "") or "")
    color_tag       = str(row.get("color_tag", "") or "")
    observations    = int(row.get("observations", 0) or 0)
    countries_raw   = str(row.get("countries", "") or "")
    conservation_st = str(row.get("conservation_status", "NE") or "NE").upper().strip()
    source_queries  = str(row.get("source_queries", "") or "")

    # Nombre público
    public_name = scientific_name
    if common_names:
        first = common_names.split("|")[0].strip()
        if first:
            public_name = first

    # Tipo de organismo
    tipo = _CLASS_INTRO.get(taxon_class, taxon_class.lower() if taxon_class else "especie")

    # Hábitat
    habitat_phrase = "diversos ecosistemas"
    for key, phrase in _HABITAT_PHRASE.items():
        if key in habitat_tag.lower():
            habitat_phrase = phrase
            break

    # Color
    color_desc = ""
    if color_tag and "unknown" not in color_tag:
        first_color = color_tag.split()[0]
        color_desc = f" Su coloración predominante es **{first_color}**."

    # Tamaño
    size_desc = ""
    if size_tag and "unknown" not in size_tag:
        if "large" in size_tag or "grande" in size_tag:
            size_desc = "de gran tamaño"
        elif "small" in size_tag or "pequeño" in size_tag or "tiny" in size_tag:
            size_desc = "de pequeño tamaño"
        else:
            size_desc = "de tamaño mediano"

    # Países
    country_list = [c.strip() for c in countries_raw.split(",") if c.strip()]
    if len(country_list) > 3:
        countries_desc = f"{', '.join(country_list[:3])} y otros {len(country_list)-3} países"
    elif country_list:
        countries_desc = ", ".join(country_list)
    else:
        countries_desc = "diversas regiones"

    # Observaciones
    if observations >= 1000:
        obs_desc = f"más de {observations:,} observaciones registradas"
    elif observations > 0:
        obs_desc = f"{observations} observaciones en el dataset"
    else:
        obs_desc = "observaciones escasas en el dataset"

    # Conservación
    conservation_phrase = _CONSERVATION_PHRASE.get(
        conservation_st,
        "con estado de conservación pendiente de evaluación",
    )

    # Oraciones finales
    sentence_1 = (
        f"**{public_name}** (*{scientific_name}*) es un {tipo} "
        f"perteneciente a la familia **{family}**, "
        f"{'adaptado' if 'us' not in scientific_name.lower() else 'adaptada'} "
        f"a {habitat_phrase}."
    )
    sentence_2 = (
        f"{'Es ' + size_desc + ', y' if size_desc else 'Con'}"
        f"{color_desc if color_desc else ' características propias de su grupo,'} "
        f"cuenta con {obs_desc} en {countries_desc}."
    )
    sentence_3 = (
        f"Según los datos de conservación disponibles, está {conservation_phrase}, "
        f"lo que la convierte en una pieza {'valiosa' if conservation_st in ('LC','NT') else 'urgente'} "
        f"para el estudio y la protección de la biodiversidad global."
    )

    return f"{sentence_1} {sentence_2} {sentence_3}"
