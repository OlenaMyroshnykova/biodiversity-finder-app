"""Carga de imágenes de especies desde GBIF."""

from __future__ import annotations

from typing import Any

import requests
import streamlit as st


GBIF_OCCURRENCE_SEARCH_URL = "https://api.gbif.org/v1/occurrence/search"


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def find_species_image_url(scientific_name: str) -> str | None:
    """
    Busca una imagen de una especie en GBIF.

    Args:
        scientific_name: Nombre científico de la especie.

    Returns:
        URL de imagen si existe, o None si no se encuentra.
    """
    if not scientific_name or not scientific_name.strip():
        return None

    params = {
        "scientificName": scientific_name,
        "mediaType": "StillImage",
        "limit": 8,
    }

    try:
        response = requests.get(
            GBIF_OCCURRENCE_SEARCH_URL,
            params=params,
            timeout=8,
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    payload = response.json()
    records = payload.get("results", [])

    for record in records:
        image_url = extract_image_url_from_occurrence(record)
        if image_url:
            return image_url

    return None


def extract_image_url_from_occurrence(record: dict[str, Any]) -> str | None:
    """
    Extrae una URL de imagen desde un registro de occurrence de GBIF.

    GBIF puede devolver imágenes en varios campos:
    - media[].identifier
    - media[].references
    - associatedMedia

    Args:
        record: Registro JSON de GBIF.

    Returns:
        URL de imagen si existe, o None.
    """
    media_items = record.get("media", [])

    if isinstance(media_items, list):
        for media_item in media_items:
            if not isinstance(media_item, dict):
                continue

            for key in ("identifier", "references"):
                value = media_item.get(key)

                if is_image_url(value):
                    return value

    associated_media = record.get("associatedMedia")

    if isinstance(associated_media, str):
        candidates = [
            item.strip()
            for item in associated_media.replace("|", ";").split(";")
        ]

        for candidate in candidates:
            if is_image_url(candidate):
                return candidate

    return None


def is_image_url(value: Any) -> bool:
    """
    Comprueba si un valor parece una URL de imagen.
    """
    if not isinstance(value, str):
        return False

    normalized = value.lower().strip()

    if not normalized.startswith(("http://", "https://")):
        return False

    image_extensions = (".jpg", ".jpeg", ".png", ".webp", ".gif")

    return any(extension in normalized for extension in image_extensions)
