"""Species image loading helpers.

Deadline-safe strategy:
- artifact URLs are preferred by the UI when they exist;
- remote lookup prefers Wikimedia/Wikipedia images for the visible cards;
- GBIF occurrence images remain available as fallback, but the app can request
  Wikimedia-first lookup to avoid random habitat/field photos.
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from typing import Any
from urllib.parse import quote

import requests

GBIF_OCCURRENCE_URL = "https://api.gbif.org/v1/occurrence/search"
GBIF_SPECIES_MATCH_URL = "https://api.gbif.org/v1/species/match"
WIKIMEDIA_API_URL = "https://commons.wikimedia.org/w/api.php"
WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary"

REQUEST_TIMEOUT_SECONDS = 8

BAD_IMAGE_MARKERS = (
    "placeholder",
    "no_image",
    "noimage",
    "default",
    "missing",
    "logo",
    "icon",
    "map.svg",
    "range_map",
    "distribution",
)

VALID_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
BAD_IMAGE_EXTENSIONS = (".svg", ".gif", ".pdf", ".html")


def find_species_image_url(
    scientific_name: str,
    *,
    excluded_urls: set[str] | None = None,
    prefer_wikimedia: bool = False,
) -> str | None:
    """Return one reliable image URL for a species.

    `prefer_wikimedia=True` is used by the Streamlit cards because GBIF
    occurrence photos can be correct technically but visually poor for a card
    (tiny animal hidden in habitat, traps, maps, etc.).
    """
    excluded_urls = excluded_urls or set()
    candidate_urls = find_species_image_candidates(
        scientific_name,
        prefer_wikimedia=prefer_wikimedia,
    )

    for image_url in candidate_urls:
        if image_url in excluded_urls:
            continue
        if is_valid_image_url(image_url):
            return image_url

    return None


# Keep cache_clear available for tests and to avoid repeated API calls.
find_species_image_url = lru_cache(maxsize=2048)(find_species_image_url)  # type: ignore[assignment]


@lru_cache(maxsize=2048)
def find_species_image_candidates(
    scientific_name: str,
    *,
    prefer_wikimedia: bool = False,
) -> tuple[str, ...]:
    """Return candidate URLs in a controlled order."""
    names_to_try = build_image_search_names(scientific_name)
    wikimedia_urls: list[str] = []
    gbif_urls: list[str] = []

    for name in names_to_try:
        wikimedia_url = fetch_wikipedia_summary_image(name)
        if wikimedia_url:
            wikimedia_urls.append(wikimedia_url)

        wikimedia_file_url = search_wikimedia_file(name)
        if wikimedia_file_url:
            wikimedia_urls.append(wikimedia_file_url)

        gbif_urls.extend(fetch_gbif_occurrence_images(name))

    usage_key = fetch_gbif_usage_key(scientific_name)
    if usage_key:
        gbif_urls.extend(fetch_gbif_occurrence_images_by_taxon_key(usage_key))

    wikimedia_urls = [url for url in deduplicate_preserving_order(wikimedia_urls) if is_valid_image_url(url)]
    gbif_urls = [url for url in deduplicate_preserving_order(gbif_urls) if is_valid_image_url(url)]

    if prefer_wikimedia:
        return tuple(deduplicate_preserving_order(wikimedia_urls + gbif_urls))

    # Backwards-compatible default for existing tests: GBIF first, Wikimedia fallback.
    return tuple(deduplicate_preserving_order(gbif_urls + wikimedia_urls))


def build_image_search_names(scientific_name: str) -> list[str]:
    """Build search names from specific to general."""
    cleaned_name = clean_scientific_name(scientific_name)
    canonical_name = canonicalize_scientific_name(cleaned_name)
    binomial_name = build_binomial_name(canonical_name)

    names = [
        cleaned_name,
        canonical_name,
        binomial_name,
    ]

    return [name for name in deduplicate_preserving_order(names) if name]


def fetch_wikipedia_summary_image(scientific_name: str) -> str | None:
    """Try the Wikipedia page summary thumbnail/original image."""
    clean_name = canonicalize_scientific_name(scientific_name)
    if not clean_name:
        return None

    url = f"{WIKIPEDIA_SUMMARY_URL}/{quote(clean_name.replace(' ', '_'))}"
    payload = fetch_json(url)
    if not payload:
        return None

    for key in ("originalimage", "thumbnail"):
        image = payload.get(key)
        if isinstance(image, dict):
            candidate = image.get("source")
            if isinstance(candidate, str) and is_valid_image_url(candidate):
                return candidate

    return None


def fetch_gbif_occurrence_images(scientific_name: str, limit: int = 10) -> list[str]:
    """Search GBIF occurrence images by scientific name."""
    if not scientific_name:
        return []

    payload = fetch_json(
        GBIF_OCCURRENCE_URL,
        params={
            "scientificName": scientific_name,
            "mediaType": "StillImage",
            "limit": limit,
        },
    )
    if not payload:
        return []

    return extract_image_urls_from_gbif_occurrences(payload)


def fetch_gbif_occurrence_images_by_taxon_key(
    taxon_key: int,
    limit: int = 10,
) -> list[str]:
    """Search GBIF occurrence images by taxonKey."""
    payload = fetch_json(
        GBIF_OCCURRENCE_URL,
        params={
            "taxonKey": taxon_key,
            "mediaType": "StillImage",
            "limit": limit,
        },
    )
    if not payload:
        return []

    return extract_image_urls_from_gbif_occurrences(payload)


def extract_image_urls_from_gbif_occurrences(payload: dict[str, Any]) -> list[str]:
    """Extract image URLs from a GBIF occurrence search payload."""
    urls: list[str] = []
    for record in payload.get("results", []):
        if isinstance(record, dict):
            url = extract_image_url_from_gbif_record(record)
            if url:
                urls.append(url)
    return urls


def extract_image_url_from_gbif_record(record: dict[str, Any]) -> str | None:
    """Extract the first usable image URL from one GBIF occurrence record."""
    media_items = record.get("media", [])
    if not isinstance(media_items, list):
        return None

    for media_item in media_items:
        if not isinstance(media_item, dict):
            continue
        identifier = media_item.get("identifier") or media_item.get("references")
        if isinstance(identifier, str) and is_valid_image_url(identifier):
            return identifier
    return None


def fetch_gbif_usage_key(scientific_name: str) -> int | None:
    """Get GBIF usageKey from Species Match."""
    cleaned_name = clean_scientific_name(scientific_name)
    if not cleaned_name:
        return None

    payload = fetch_json(GBIF_SPECIES_MATCH_URL, params={"name": cleaned_name})
    if not payload:
        return None

    usage_key = payload.get("usageKey")
    if isinstance(usage_key, int):
        return usage_key
    return None


def search_wikimedia_file(scientific_name: str) -> str | None:
    """Search Wikimedia Commons for a representative image."""
    clean_name = canonicalize_scientific_name(scientific_name)
    if not clean_name:
        return None

    payload = fetch_json(
        WIKIMEDIA_API_URL,
        params={
            "action": "query",
            "generator": "search",
            "gsrsearch": clean_name,
            "gsrnamespace": 6,
            "gsrlimit": 6,
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
            "iiurlwidth": 700,
            "format": "json",
        },
    )
    if not payload:
        return None

    pages = payload.get("query", {}).get("pages", [])
    if isinstance(pages, dict):
        page_values = list(pages.values())
    elif isinstance(pages, list):
        page_values = pages
    else:
        page_values = []

    for page in page_values:
        if not isinstance(page, dict):
            continue
        title = str(page.get("title", ""))
        if any(marker in title.lower() for marker in BAD_IMAGE_MARKERS):
            continue
        image_info = page.get("imageinfo", [])
        if not isinstance(image_info, list) or not image_info:
            continue
        info = image_info[0]
        if not isinstance(info, dict):
            continue
        mime = str(info.get("mime", "")).lower()
        if mime and not mime.startswith("image/"):
            continue
        candidate = info.get("thumburl") or info.get("url")
        if isinstance(candidate, str) and is_valid_image_url(candidate):
            return candidate

    return None


def fetch_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Download JSON using requests with a safe timeout."""
    try:
        response = requests.get(
            url,
            params=params,
            headers={
                "User-Agent": "biodiversity-finder-app/1.0",
                "Accept": "application/json",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            return payload
    except Exception:
        return None
    return None


def is_valid_image_url(image_url: str) -> bool:
    """Validate image-like URLs and reject obvious placeholders/maps."""
    normalized_url = str(image_url or "").strip().lower()
    if not normalized_url.startswith(("http://", "https://")):
        return False
    if any(marker in normalized_url for marker in BAD_IMAGE_MARKERS):
        return False
    if any(normalized_url.split("?")[0].endswith(ext) for ext in BAD_IMAGE_EXTENSIONS):
        return False

    clean_url = normalized_url.split("?")[0]
    if clean_url.endswith(VALID_IMAGE_EXTENSIONS):
        return True

    # Wikimedia thumbnail URLs sometimes contain encoded file names and params.
    if "upload.wikimedia.org" in normalized_url and any(ext in normalized_url for ext in VALID_IMAGE_EXTENSIONS):
        return True

    # Keep remote artifact URLs that may be image services without an extension.
    return any(domain in normalized_url for domain in ("inaturalist", "staticflickr", "wikimedia"))


# Backwards-compatible alias used by older code/tests.
def is_probably_valid_image_url(image_url: str) -> bool:
    """Alias for old code path."""
    return is_valid_image_url(image_url)


def clean_scientific_name(scientific_name: str) -> str:
    """Normalize scientific-name text."""
    return re.sub(r"\s+", " ", str(scientific_name or "").strip())


def canonicalize_scientific_name(scientific_name: str) -> str:
    """Remove parenthesized authorship and normalize spaces."""
    text = clean_scientific_name(scientific_name)
    text = re.sub(r"\s*\([^)]*\)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_binomial_name(scientific_name: str) -> str:
    """Return genus + species if available."""
    parts = clean_scientific_name(scientific_name).split()
    if len(parts) >= 2:
        return " ".join(parts[:2])
    return clean_scientific_name(scientific_name)


def deduplicate_preserving_order(values: list[str]) -> list[str]:
    """Remove duplicates without changing order."""
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
