"""Validación de URLs de imágenes."""

from __future__ import annotations

from urllib.parse import urlparse


VALID_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
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


def is_valid_image_url(image_url: object) -> bool:
    """Comprueba si una URL parece una imagen usable."""
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

    trusted_domains = (
        "wikimedia.org",
        "wikipedia.org",
        "gbif.org",
        "inaturalist-open-data.s3.amazonaws.com",
        "static.inaturalist.org",
    )

    return any(domain in parsed_url.netloc.lower() for domain in trusted_domains)
