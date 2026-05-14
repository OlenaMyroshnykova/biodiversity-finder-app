"""Species image loading helpers.

Deadline-safe strategy:
- the UI first uses image URLs already present in the artifact;
- if the artifact has no usable image, remote lookup prefers Wikipedia/Wikimedia;
- GBIF occurrence images are used only as the last remote fallback because they
  are often habitat photos where the animal is barely visible.
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from typing import Any, Iterable
from urllib.parse import quote

import requests

GBIF_OCCURRENCE_URL = "https://api.gbif.org/v1/occurrence/search"
GBIF_SPECIES_MATCH_URL = "https://api.gbif.org/v1/species/match"
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
WIKIMEDIA_API_URL = "https://commons.wikimedia.org/w/api.php"
WIKIPEDIA_API_TEMPLATE = "https://{lang}.wikipedia.org/w/api.php"
WIKIPEDIA_SUMMARY_TEMPLATE = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
COMMONS_FILEPATH_URL = "https://commons.wikimedia.org/wiki/Special:FilePath/{filename}"

REQUEST_TIMEOUT_SECONDS = float(os.getenv("REMOTE_IMAGE_TIMEOUT_SECONDS", "2.5"))
WIKIPEDIA_LANGUAGES = ("en", "es")


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _deep_image_lookup_enabled() -> bool:
    """Whether to use slow fallback providers such as Commons search and GBIF.

    The deadline default is fast mode: Wikipedia summary + Wikidata P18 only.
    This avoids many network calls per card. Set DEEP_IMAGE_LOOKUP=true only
    when you have time to wait and want more image coverage.
    """
    return _env_bool("DEEP_IMAGE_LOOKUP", True)

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
    "locator_map",
    "blank",
    "question_mark",
)

VALID_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
BAD_IMAGE_EXTENSIONS = (".svg", ".gif", ".pdf", ".html")


def find_species_image_url(
    scientific_name: str,
    *,
    common_names: str = "",
    excluded_urls: set[str] | None = None,
    prefer_wikimedia: bool = False,
) -> str | None:
    """Return one reliable image URL for a species.

    Parameters stay backwards-compatible with older tests. The cache lives in
    ``find_species_image_candidates`` so ``excluded_urls`` can be a normal set.
    """
    excluded_urls = excluded_urls or set()
    candidate_urls = find_species_image_candidates(
        scientific_name,
        common_names=common_names,
        prefer_wikimedia=prefer_wikimedia,
    )

    for image_url in candidate_urls:
        if image_url in excluded_urls:
            continue
        if is_valid_image_url(image_url):
            return image_url
    return None


def _clear_image_caches() -> None:
    find_species_image_candidates.cache_clear()  # type: ignore[attr-defined]
    fetch_wikipedia_summary_image.cache_clear()  # type: ignore[attr-defined]
    search_wikipedia_page_image.cache_clear()  # type: ignore[attr-defined]
    search_wikidata_p18_image.cache_clear()  # type: ignore[attr-defined]

    # search_wikimedia_file is intentionally not cached directly.
    # This avoids stale Wikimedia results in tests that monkeypatch requests.get.
    cache_clear = getattr(search_wikimedia_file, "cache_clear", None)
    if callable(cache_clear):
        cache_clear()
    fetch_gbif_usage_key.cache_clear()  # type: ignore[attr-defined]
    fetch_gbif_occurrence_images.cache_clear()  # type: ignore[attr-defined]
    fetch_gbif_occurrence_images_by_taxon_key.cache_clear()  # type: ignore[attr-defined]


# Compatibility: several tests call ``find_species_image_url.cache_clear()``.
find_species_image_url.cache_clear = _clear_image_caches  # type: ignore[attr-defined]


@lru_cache(maxsize=2048)
def find_species_image_candidates(
    scientific_name: str,
    *,
    common_names: str = "",
    prefer_wikimedia: bool = False,
) -> tuple[str, ...]:
    """Return image candidates without making the page painfully slow.

    Fast default for the Streamlit app:
    - try only the most useful names, not every alias;
    - use Wikipedia summary and Wikidata P18 first;
    - skip Commons search and GBIF unless DEEP_IMAGE_LOOKUP=true.

    This keeps remote lookup acceptable even when REMOTE_IMAGE_LOOKUP_LIMIT is
    temporarily raised for the demo.
    """
    names_to_try = build_image_search_names(scientific_name, common_names)
    fast_names = names_to_try[:2]  # full/canonical + binomial/common fallback
    deep_lookup = _deep_image_lookup_enabled()

    wikipedia_urls: list[str] = []
    wikidata_urls: list[str] = []
    commons_urls: list[str] = []
    gbif_urls: list[str] = []

    for name in fast_names:
        for language in WIKIPEDIA_LANGUAGES:
            summary_url = fetch_wikipedia_summary_image(name, language)
            if summary_url:
                wikipedia_urls.append(summary_url)

        p18_url = search_wikidata_p18_image(name)
        if p18_url:
            wikidata_urls.append(p18_url)

    if deep_lookup:
        for name in names_to_try[:3]:
            for language in WIKIPEDIA_LANGUAGES:
                page_image_url = search_wikipedia_page_image(name, language)
                if page_image_url:
                    wikipedia_urls.append(page_image_url)

            commons_url = search_wikimedia_file(name)
            if commons_url:
                commons_urls.append(commons_url)

        # GBIF is intentionally last for visible cards. It is useful, but often
        # returns field/habitat shots rather than clean encyclopedia images.
        for name in names_to_try[:2]:
            gbif_urls.extend(fetch_gbif_occurrence_images(name, limit=3))

        usage_key = fetch_gbif_usage_key(scientific_name)
        if usage_key:
            gbif_urls.extend(fetch_gbif_occurrence_images_by_taxon_key(usage_key, limit=3))

    wikipedia_urls = valid_unique_urls(wikipedia_urls)
    wikidata_urls = valid_unique_urls(wikidata_urls)
    commons_urls = valid_unique_urls(commons_urls)
    gbif_urls = valid_unique_urls(gbif_urls)

    if prefer_wikimedia:
        return tuple(deduplicate_preserving_order(wikipedia_urls + wikidata_urls + commons_urls + gbif_urls))

    # Backwards-compatible default for older code/tests. In fast mode this no
    # longer forces slow GBIF calls; gbif_urls is empty unless deep lookup is on.
    return tuple(deduplicate_preserving_order(gbif_urls + wikipedia_urls + wikidata_urls + commons_urls))


def build_image_search_names(scientific_name: str, common_names: str = "") -> list[str]:
    """Build search names from specific to general.

    Important: use the canonical binomial before the full scientific name with
    authorship, e.g. ``Gerbillus nanus`` before ``Gerbillus nanus Blanford``.
    """
    cleaned_name = clean_scientific_name(scientific_name)
    canonical_name = canonicalize_scientific_name(cleaned_name)
    binomial_name = build_binomial_name(canonical_name)
    common_name_values = extract_common_name_values(common_names)

    # Keep the original full name first for compatibility and for very specific taxa.
    # Remote providers still canonicalize internally before building URLs/queries,
    # so authorship does not break Wikipedia/Wikidata lookup.
    names = [cleaned_name, canonical_name, binomial_name, *common_name_values[:4]]
    return [name for name in deduplicate_preserving_order(names) if len(name) >= 3]


@lru_cache(maxsize=4096)
def fetch_wikipedia_summary_image(search_name: str, language: str = "en") -> str | None:
    """Try Wikipedia REST summary thumbnail/original image."""
    clean_name = canonicalize_scientific_name(search_name)
    if not clean_name:
        return None

    url = WIKIPEDIA_SUMMARY_TEMPLATE.format(lang=language, title=quote(clean_name.replace(" ", "_")))
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


@lru_cache(maxsize=4096)
def search_wikipedia_page_image(search_name: str, language: str = "en") -> str | None:
    """Search Wikipedia pages and return their page image if available."""
    clean_name = canonicalize_scientific_name(search_name)
    if not clean_name:
        return None

    payload = fetch_json(
        WIKIPEDIA_API_TEMPLATE.format(lang=language),
        params={
            "action": "query",
            "generator": "search",
            "gsrsearch": clean_name,
            "gsrnamespace": 0,
            "gsrlimit": 3,
            "prop": "pageimages",
            "piprop": "thumbnail|original",
            "pithumbsize": 900,
            "format": "json",
            "formatversion": 2,
        },
    )
    if not payload:
        return None

    pages = payload.get("query", {}).get("pages", [])
    if not isinstance(pages, list):
        return None

    for page in pages:
        if not isinstance(page, dict):
            continue
        image = page.get("original") or page.get("thumbnail")
        if isinstance(image, dict):
            candidate = image.get("source")
            if isinstance(candidate, str) and is_valid_image_url(candidate):
                return candidate
    return None


@lru_cache(maxsize=4096)
def search_wikidata_p18_image(search_name: str) -> str | None:
    """Search Wikidata and return P18 image via Commons Special:FilePath."""
    clean_name = canonicalize_scientific_name(search_name)
    if not clean_name:
        return None

    search_payload = fetch_json(
        WIKIDATA_API_URL,
        params={
            "action": "wbsearchentities",
            "search": clean_name,
            "language": "en",
            "format": "json",
            "limit": 3,
        },
    )
    if not search_payload:
        return None

    entity_ids = [item.get("id") for item in search_payload.get("search", []) if isinstance(item, dict)]
    entity_ids = [entity_id for entity_id in entity_ids if isinstance(entity_id, str)]
    if not entity_ids:
        return None

    entity_payload = fetch_json(
        WIKIDATA_API_URL,
        params={
            "action": "wbgetentities",
            "ids": "|".join(entity_ids[:3]),
            "props": "claims",
            "format": "json",
        },
    )
    if not entity_payload:
        return None

    entities = entity_payload.get("entities", {})
    if not isinstance(entities, dict):
        return None

    for entity in entities.values():
        if not isinstance(entity, dict):
            continue
        claims = entity.get("claims", {})
        p18_claims = claims.get("P18", []) if isinstance(claims, dict) else []
        if not isinstance(p18_claims, list):
            continue
        for claim in p18_claims:
            try:
                filename = claim["mainsnak"]["datavalue"]["value"]
            except Exception:
                continue
            if isinstance(filename, str):
                candidate = COMMONS_FILEPATH_URL.format(filename=quote(filename.replace(" ", "_")))
                if is_valid_image_url(candidate):
                    return candidate
    return None


def search_wikimedia_file(search_name: str) -> str | None:
    """Search Wikimedia Commons files for a representative image."""
    clean_name = canonicalize_scientific_name(search_name)
    if not clean_name:
        return None

    payload = fetch_json(
        WIKIMEDIA_API_URL,
        params={
            "action": "query",
            "generator": "search",
            "gsrsearch": f'"{clean_name}"',
            "gsrnamespace": 6,
            "gsrlimit": 8,
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
            "iiurlwidth": 900,
            "format": "json",
            "formatversion": 2,
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
        width = int(info.get("thumbwidth") or info.get("width") or 0)
        height = int(info.get("thumbheight") or info.get("height") or 0)
        if mime and not mime.startswith("image/"):
            continue
        if width and height and (width < 120 or height < 120):
            continue
        candidate = info.get("thumburl") or info.get("url")
        if isinstance(candidate, str) and is_valid_image_url(candidate):
            return candidate
    return None


@lru_cache(maxsize=4096)
def fetch_gbif_occurrence_images(scientific_name: str, limit: int = 10) -> tuple[str, ...]:
    """Search GBIF occurrence images by scientific name."""
    if not scientific_name:
        return tuple()

    payload = fetch_json(
        GBIF_OCCURRENCE_URL,
        params={
            "scientificName": scientific_name,
            "mediaType": "StillImage",
            "limit": limit,
        },
    )
    if not payload:
        return tuple()
    return tuple(extract_image_urls_from_gbif_occurrences(payload))


@lru_cache(maxsize=4096)
def fetch_gbif_occurrence_images_by_taxon_key(taxon_key: int, limit: int = 10) -> tuple[str, ...]:
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
        return tuple()
    return tuple(extract_image_urls_from_gbif_occurrences(payload))


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


@lru_cache(maxsize=4096)
def fetch_gbif_usage_key(scientific_name: str) -> int | None:
    """Get GBIF usageKey from Species Match."""
    cleaned_name = build_binomial_name(canonicalize_scientific_name(scientific_name))
    if not cleaned_name:
        return None

    payload = fetch_json(GBIF_SPECIES_MATCH_URL, params={"name": cleaned_name})
    if not payload:
        return None

    usage_key = payload.get("usageKey")
    return usage_key if isinstance(usage_key, int) else None


def fetch_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Download JSON using requests with a safe timeout."""
    try:
        response = requests.get(
            url,
            params=params,
            headers={
                "User-Agent": "biodiversity-finder-app/1.0 (educational project)",
                "Accept": "application/json",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def is_valid_image_url(image_url: str) -> bool:
    """Validate image-like URLs and reject obvious placeholders/maps/icons."""
    normalized_url = str(image_url or "").strip().lower()
    if not normalized_url.startswith(("http://", "https://")):
        return False
    if any(marker in normalized_url for marker in BAD_IMAGE_MARKERS):
        return False
    clean_url = normalized_url.split("?")[0]
    if any(clean_url.endswith(ext) for ext in BAD_IMAGE_EXTENSIONS):
        return False
    if clean_url.endswith(VALID_IMAGE_EXTENSIONS):
        return True
    if "upload.wikimedia.org" in normalized_url and any(ext in normalized_url for ext in VALID_IMAGE_EXTENSIONS):
        return True
    if "commons.wikimedia.org/wiki/special:filepath" in normalized_url and any(ext in normalized_url for ext in VALID_IMAGE_EXTENSIONS):
        return True
    return any(domain in normalized_url for domain in ("inaturalist", "staticflickr", "wikimedia", "wikimedia.org"))


# Backwards-compatible alias used by older code/tests.
def is_probably_valid_image_url(image_url: str) -> bool:
    """Alias for old code path."""
    return is_valid_image_url(image_url)


def clean_scientific_name(scientific_name: str) -> str:
    """Normalize scientific-name text."""
    return re.sub(r"\s+", " ", str(scientific_name or "").strip())


def canonicalize_scientific_name(scientific_name: str) -> str:
    """Remove authorship/year fragments and normalize spaces."""
    text = clean_scientific_name(scientific_name)
    text = re.sub(r"\s*\([^)]*\)", "", text)
    text = re.sub(r"\b[A-Z][a-z]+,?\s+\d{4}\b", "", text)
    text = re.sub(r"\b\d{4}\b", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_binomial_name(scientific_name: str) -> str:
    """Return genus + species if available."""
    parts = clean_scientific_name(scientific_name).split()
    if len(parts) >= 2:
        return " ".join(parts[:2])
    return clean_scientific_name(scientific_name)


def extract_common_name_values(common_names: str) -> list[str]:
    """Extract a small list of common names from pipe/comma/slash text."""
    if not common_names:
        return []
    raw_parts = re.split(r"[|,/;]", str(common_names))
    values: list[str] = []
    for part in raw_parts:
        cleaned = re.sub(r"\s+", " ", part).strip()
        if not cleaned or len(cleaned) < 3:
            continue
        if re.search(r"[А-Яа-яІіЇїЄєҐґ]", cleaned):
            # Keep the demo search Spanish/English-oriented for external lookup;
            # Cyrillic names still work for text fallback if present in artifact.
            continue
        values.append(cleaned)
    return deduplicate_preserving_order(values)


def valid_unique_urls(urls: Iterable[str]) -> list[str]:
    """Return valid URLs without duplicates."""
    return [url for url in deduplicate_preserving_order(list(urls)) if is_valid_image_url(url)]


def deduplicate_preserving_order(values: list[str]) -> list[str]:
    """Remove duplicates without changing order."""
    unique_values: list[str] = []
    seen: set[str] = set()
    for value in values:
        value = str(value or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        unique_values.append(value)
    return unique_values
