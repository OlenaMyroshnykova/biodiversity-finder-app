"""Servicio de imágenes con fallback."""

from __future__ import annotations

import streamlit as st

from src.image_sources.gbif import find_gbif_image_url
from src.image_sources.wikimedia import find_wikimedia_image_url


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def find_species_image_url(scientific_name: str) -> str | None:
    """Busca imagen primero en GBIF y después en Wikimedia Commons."""
    clean_name = str(scientific_name).strip()

    if not clean_name:
        return None

    gbif_image_url = find_gbif_image_url(clean_name)
    if gbif_image_url:
        return gbif_image_url

    return find_wikimedia_image_url(clean_name)
