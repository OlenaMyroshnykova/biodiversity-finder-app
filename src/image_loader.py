"""Carga de imágenes de especies.

Objetivo:
- evitar que una búsqueda devuelva siempre la misma foto;
- preferir imágenes asociadas a la especie exacta;
- permitir excluir URLs ya usadas en la página;
- devolver None si no hay una imagen razonable.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from urllib.parse import quote
from urllib.request import Request, urlopen


GBIF_OCCURRENCE_SEARCH_URL = "https://api.gbif.org/v1/occurrence/search"
GBIF_SPECIES_MATCH_URL = "https://api.gbif.org/v1/species/match"

REQUEST_TIMEOUT_SECONDS = 8

BAD_IMAGE_MARKERS = [
    "placeholder",
    "no_image",
    "noimage",
    "default",
    "missing",
]


def find_species_image_url(
    scientific_name: str,
    *,
    excluded_urls: set[str] | None = None,
) -> str | None:
    """Busca una imagen para una especie.

    `excluded_urls` permite que la UI no repita la misma foto en varias tarjetas.
    """
    excluded_urls = excluded_urls or set()

    candidate_urls = find_species_image_candidates(scientific_name)

    for image_url in candidate_urls:
        if image_url in excluded_urls:
            continue

        if is_probably_valid_image_url(image_url):
            return image_url

    return None


@lru_cache(maxsize=2048)
def find_species_image_candidates(scientific_name: str) -> tuple[str, ...]:
    """Devuelve URLs candidatas en orden de preferencia."""
    names_to_try = build_image_search_names(scientific_name)
    collected_urls: list[str] = []

    for name in names_to_try:
        collected_urls.extend(fetch_gbif_occurrence_images(name))

    # Fallback por usageKey cuando GBIF encuentra taxon exacto.
    usage_key = fetch_gbif_usage_key(scientific_name)

    if usage_key:
        collected_urls.extend(fetch_gbif_occurrence_images_by_taxon_key(usage_key))

    unique_urls = deduplicate_preserving_order(collected_urls)

    return tuple(unique_urls)


def build_image_search_names(scientific_name: str) -> list[str]:
    """Construye nombres de búsqueda de más específico a más general."""
    cleaned_name = clean_scientific_name(scientific_name)
    canonical_name = canonicalize_scientific_name(cleaned_name)
    binomial_name = build_binomial_name(canonical_name)

    names = [
        cleaned_name,
        canonical_name,
        binomial_name,
    ]

    return [
        name
        for name in deduplicate_preserving_order(names)
        if name
    ]


def fetch_gbif_occurrence_images(scientific_name: str, limit: int = 20) -> list[str]:
    """Busca imágenes en occurrences de GBIF por nombre científico."""
    if not scientific_name:
        return []

    query_url = (
        f"{GBIF_OCCURRENCE_SEARCH_URL}"
        f"?scientificName={quote(scientific_name)}"
        f"&mediaType=StillImage"
        f"&limit={limit}"
    )

    payload = fetch_json(query_url)

    if not payload:
        return []

    return extract_image_urls_from_gbif_occurrences(payload)


def fetch_gbif_occurrence_images_by_taxon_key(
    taxon_key: int,
    limit: int = 20,
) -> list[str]:
    """Busca imágenes en occurrences de GBIF por taxonKey."""
    query_url = (
        f"{GBIF_OCCURRENCE_SEARCH_URL}"
        f"?taxonKey={taxon_key}"
        f"&mediaType=StillImage"
        f"&limit={limit}"
    )

    payload = fetch_json(query_url)

    if not payload:
        return []

    return extract_image_urls_from_gbif_occurrences(payload)


def fetch_gbif_usage_key(scientific_name: str) -> int | None:
    """Obtiene usageKey desde GBIF Species Match."""
    cleaned_name = clean_scientific_name(scientific_name)

    if not cleaned_name:
        return None

    query_url = f"{GBIF_SPECIES_MATCH_URL}?name={quote(cleaned_name)}"
    payload = fetch_json(query_url)

    if not payload:
        return None

    usage_key = payload.get("usageKey")

    if isinstance(usage_key, int):
        return usage_key

    return None


def extract_image_urls_from_gbif_occurrences(payload: dict) -> list[str]:
    """Extrae URLs de media desde respuesta de GBIF occurrence search."""
    urls: list[str] = []

    for record in payload.get("results", []):
        media_items = record.get("media", [])

        for media_item in media_items:
            identifier = media_item.get("identifier") or media_item.get("references")

            if isinstance(identifier, str) and identifier.startswith(("http://", "https://")):
                urls.append(identifier)

    return urls


def fetch_json(url: str) -> dict | None:
    """Descarga JSON usando urllib para no añadir dependencias extra."""
    try:
        request = Request(
            url,
            headers={
                "User-Agent": "biodiversity-finder-app/1.0",
                "Accept": "application/json",
            },
        )

        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def is_probably_valid_image_url(image_url: str) -> bool:
    """Filtra URLs que claramente no son buenas imágenes."""
    normalized_url = image_url.lower()

    if not normalized_url.startswith(("http://", "https://")):
        return False

    if any(marker in normalized_url for marker in BAD_IMAGE_MARKERS):
        return False

    return True


def clean_scientific_name(scientific_name: str) -> str:
    """Normaliza texto del nombre científico."""
    return re.sub(r"\s+", " ", str(scientific_name or "").strip())


def canonicalize_scientific_name(scientific_name: str) -> str:
    """Quita autoría entre paréntesis y espacios extra."""
    text = clean_scientific_name(scientific_name)
    text = re.sub(r"\s*\([^)]*\)", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def build_binomial_name(scientific_name: str) -> str:
    """Devuelve género + especie si existen."""
    parts = clean_scientific_name(scientific_name).split()

    if len(parts) >= 2:
        return " ".join(parts[:2])

    return clean_scientific_name(scientific_name)


def deduplicate_preserving_order(values: list[str]) -> list[str]:
    """Elimina duplicados conservando orden."""
    unique_values: list[str] = []
    seen: set[str] = set()

    for value in values:
        value = str(value or "").strip()

        if not value:
            continue

        if value in seen:
            continue

        seen.add(value)
        unique_values.append(value)

    return unique_values
