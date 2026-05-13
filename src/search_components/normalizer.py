"""Text normalization for the Spanish/English demo search."""

from __future__ import annotations

import re
import unicodedata


def normalize_text(text: object) -> str:
    """Normalize text to lowercase ASCII-ish Spanish/English tokens."""

    normalized = unicodedata.normalize("NFKD", str(text).lower())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    cleaned_text = re.sub(r"[^a-z0-9\s]", " ", without_accents)
    return re.sub(r"\s+", " ", cleaned_text).strip()
