"""Carga de imágenes de especies desde GBIF y Wikimedia Commons."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import requests
import streamlit as st


GBIF_OCCURRENCE_URL = "https://api.gbif.org/v1/occurrence/search"
WIKIMEDIA_API_URL = "https://commons.wikimedia.org/w/api.php"

REQUEST_HEADERS = {
    "User-Agent": (
        "BiodiversityFinder/1.0 "
        "(educational Streamlit app; https://github.com/OlenaMyroshnykova/biodiversity-finder-app)"
    )
}

VALID_IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
)

BAD_IMAGE_MARKERS = (
    "placeholder",
    "no_image",
    "noimage",
    "missing",
    "default",
    "icon",
    "logo",
    "map",
    "range",
    "distribution",
    "svg",
)


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def find_species_image_url(scientific_name: str) -> str | None:
    """
    Busca una imagen de una especie.

    Orden de búsqueda:
    1. GBIF, porque es la fuente principal del proyecto.
    2. Wikimedia Commons, como fallback público cuando GBIF no tiene foto útil.

    Args:
        scientific_name: Nombre científico de la especie.

    Returns:
        URL de imagen o None.
    """
    clean_name = str(scientific_name).strip()

    if not clean_name:
        return None

    gbif_image_url = find_gbif_image_url(clean_name)

    if gbif_image_url:
        return gbif_image_url

    wikimedia_image_url = find_wikimedia_image_url(clean_name)

    if wikimedia_image_url:
        return wikimedia_image_url

    return None


def find_gbif_image_url(scientific_name: str) -> str | None:
    """
    Busca una imagen en GBIF.
    """
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
    """
    Extrae una URL de imagen de un registro GBIF.
    """
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


def find_wikimedia_image_url(scientific_name: str) -> str | None:
    """
    Busca una imagen en Wikimedia Commons.

    Se consulta el namespace de archivos de Commons. Este fallback ayuda mucho
    para especies populares y visualmente documentadas, como mariposas.
    """
    search_queries = build_wikimedia_search_queries(scientific_name)

    for search_query in search_queries:
        image_url = search_wikimedia_file(search_query)

        if image_url:
            return image_url

    return None


def build_wikimedia_search_queries(scientific_name: str) -> list[str]:
    """
    Construye consultas para Wikimedia Commons.
    """
    clean_name = str(scientific_name).strip()

    if not clean_name:
        return []

    queries = [
        f'intitle:"{clean_name}"',
        f'"{clean_name}"',
        f'{clean_name} species',
        f'{clean_name} animal',
    ]

    return queries


def search_wikimedia_file(search_query: str) -> str | None:
    """
    Busca un archivo de imagen en Wikimedia Commons.
    """
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": 6,
        "gsrlimit": 10,
        "prop": "imageinfo",
        "iiprop": "url|mime|size",
        "iiurlwidth": 700,
        "format": "json",
        "formatversion": 2,
    }

    try:
        response = requests.get(
            WIKIMEDIA_API_URL,
            params=params,
            headers=REQUEST_HEADERS,
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    payload = response.json()
    pages = payload.get("query", {}).get("pages", [])

    if not isinstance(pages, list):
        return None

    candidates = []

    for page in pages:
        image_info_items = page.get("imageinfo", [])

        if not image_info_items:
            continue

        image_info = image_info_items[0]
        image_url = image_info.get("thumburl") or image_info.get("url")
        mime_type = image_info.get("mime", "")
        width = image_info.get("width", 0)
        height = image_info.get("height", 0)
        title = page.get("title", "")

        if not is_valid_image_url(image_url):
            continue

        if not str(mime_type).startswith("image/"):
            continue

        quality_score = calculate_image_quality_score(
            image_url=image_url,
            title=title,
            width=width,
            height=height,
        )

        candidates.append((quality_score, image_url))

    if not candidates:
        return None

    candidates.sort(reverse=True, key=lambda item: item[0])

    return candidates[0][1]


def calculate_image_quality_score(
    *,
    image_url: str,
    title: str,
    width: int | float | None,
    height: int | float | None,
) -> float:
    """
    Calcula un score simple para elegir imágenes más útiles.
    """
    score = 0.0
    text = f"{image_url} {title}".lower()

    try:
        width_value = float(width or 0)
        height_value = float(height or 0)
    except (TypeError, ValueError):
        width_value = 0
        height_value = 0

    if width_value >= 400:
        score += 1.0

    if height_value >= 300:
        score += 1.0

    if any(extension in image_url.lower() for extension in VALID_IMAGE_EXTENSIONS):
        score += 1.0

    if "species" in text:
        score += 0.2

    if "male" in text or "female" in text:
        score += 0.1

    if any(marker in text for marker in BAD_IMAGE_MARKERS):
        score -= 2.0

    return score


def is_valid_image_url(image_url: object) -> bool:
    """
    Comprueba si una URL parece una imagen usable.
    """
    if not isinstance(image_url, str):
        return False

    clean_url = image_url.strip()

    if not clean_url:
        return False

    parsed_url = urlparse(clean_url)

    if parsed_url.scheme not in {"http", "https"}:
        return False

    lower_url = clean_url.lower()

    if any(marker in lower_url for marker in BAD_IMAGE_MARKERS):
        return False

    if lower_url.endswith(".svg"):
        return False

    if any(extension in lower_url for extension in VALID_IMAGE_EXTENSIONS):
        return True

    # Algunas URLs de Wikimedia/GBIF no terminan con extensión clara,
    # pero sí son imágenes válidas servidas por el dominio.
    trusted_domains = (
        "wikimedia.org",
        "wikipedia.org",
        "gbif.org",
        "inaturalist-open-data.s3.amazonaws.com",
        "static.inaturalist.org",
    )

    return any(domain in parsed_url.netloc.lower() for domain in trusted_domains)
