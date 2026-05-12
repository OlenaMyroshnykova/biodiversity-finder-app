"""Carga de imágenes desde GBIF."""

from __future__ import annotations

from typing import Any

import requests

from src.image_sources.validators import is_valid_image_url


GBIF_OCCURRENCE_URL = "https://api.gbif.org/v1/occurrence/search"
REQUEST_HEADERS = {
    "User-Agent": "BiodiversityFinder/1.0 educational Streamlit app"
}


def find_gbif_image_url(scientific_name: str) -> str | None:
    """Busca una imagen en GBIF."""
    params = {
        "scientificName": scientific_name,
        "mediaType": "StillImage",
        "limit": 20,
    }

    try:
        response = requests.get(
            GBIF_OCCURRENCE_URL,
            params=params,
            headers=REQUEST_HEADERS,
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    payload = response.json()
    records = payload.get("results", [])

    for record in records:
        image_url = extract_image_url_from_gbif_record(record)

        if is_valid_image_url(image_url):
            return image_url

    return None


def extract_image_url_from_gbif_record(record: dict[str, Any]) -> str | None:
    """Extrae una URL de imagen de un registro GBIF."""
    media_items = record.get("media", [])

    if isinstance(media_items, list):
        for media_item in media_items:
            if not isinstance(media_item, dict):
                continue

            for key in ("identifier", "references", "source"):
                image_url = media_item.get(key)

                if is_valid_image_url(image_url):
                    return image_url

    associated_media = record.get("associatedMedia")

    if isinstance(associated_media, str):
        for possible_url in associated_media.replace("|", "\n").splitlines():
            possible_url = possible_url.strip()

            if is_valid_image_url(possible_url):
                return possible_url

    return None
