"""Generador de fichas narrativas tipo National Geographic."""

from __future__ import annotations

import pandas as pd


def build_sighting_narrative(row: pd.Series) -> str:
    """Genera una descripción narrativa basada en datos del dataframe."""
    scientific_name = str(row.get("scientific_name", "esta especie"))
    common_names = str(row.get("vernacular_names", "") or "").strip()
    taxon_class = str(row.get("taxon_class", "grupo desconocido"))
    family = str(row.get("family", "familia desconocida"))
    habitat = str(row.get("habitat_tag", "hábitat no especificado"))
    size = str(row.get("size_tag", "tamaño no especificado"))
    color = str(row.get("color_tag", "color no especificado"))
    observations = row.get("observations", 0)
    countries = str(row.get("countries", "regiones no especificadas"))
    conservation = str(row.get("conservation_category", "estado no disponible"))

    public_name = scientific_name

    if common_names:
        public_name = common_names.split("|")[0].strip() or scientific_name

    return (
        f"Como una ficha de avistamiento, **{public_name}** "
        f"(*{scientific_name}*) aparece en el dataset como parte de la clase "
        f"**{taxon_class}** y la familia **{family}**. "
        f"Sus señales de búsqueda sugieren un perfil **{size}**, con tonos "
        f"**{color}** y asociación con hábitats como **{habitat}**. "
        f"En esta muestra se registran **{observations} observaciones**, "
        f"con presencia en **{countries}**. "
        f"Estado de conservación mostrado por la app: **{conservation}**."
    )
