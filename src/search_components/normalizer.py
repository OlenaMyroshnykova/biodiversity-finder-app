"""Normalización de texto para búsqueda multilingüe."""

from __future__ import annotations

import re
import unicodedata


def normalize_text(text: object) -> str:
    """Normaliza texto y conserva alfabetos latinos y cirílicos."""
    normalized = unicodedata.normalize("NFKD", str(text).lower())
    without_accents = "".join(
        character for character in normalized
        if not unicodedata.combining(character)
    )
    cleaned_text = re.sub(
        r"[^a-zа-яёіїєґ0-9ñç\s]",
        " ",
        without_accents,
    )

    return re.sub(r"\s+", " ", cleaned_text).strip()
