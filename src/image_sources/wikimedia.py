"""Fallback de imágenes en Wikimedia Commons."""

from __future__ import annotations

import requests

from src.image_sources.validators import is_valid_image_url


WIKIMEDIA_API_URL = "https://commons.wikimedia.org/w/api.php"
REQUEST_HEADERS = {
    "User-Agent": "BiodiversityFinder/1.0 educational Streamlit app"
}


def find_wikimedia_image_url(scientific_name: str) -> str | None:
    """Busca una imagen en Wikimedia Commons."""
    clean_name = str(scientific_name).strip()

    if not clean_name:
        return None

    queries = [
        f'intitle:"{clean_name}"',
        f'"{clean_name}"',
        f"{clean_name} species",
    ]

    for query in queries:
        image_url = search_wikimedia_file(query)

        if image_url:
            return image_url

    return None


def search_wikimedia_file(search_query: str) -> str | None:
    """Busca archivo de imagen en Wikimedia Commons."""
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

        if not is_valid_image_url(image_url):
            continue

        if not str(mime_type).startswith("image/"):
            continue

        candidates.append(image_url)

    if not candidates:
        return None

    return candidates[0]
