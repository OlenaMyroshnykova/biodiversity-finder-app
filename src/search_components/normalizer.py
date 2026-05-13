"""Text normalization for search.

The UI promises stable Spanish + English vibe-search, but the fallback name search
must still work for any common name already present in the artifact. For that
reason we keep Unicode letters such as Cyrillic inside ``vernacular_names``.
"""
from __future__ import annotations

import re
import unicodedata


def normalize_text(text: object) -> str:
    """Normalize text while preserving non-Latin alphabetic names.

    Examples:
    - "León" -> "leon"
    - "Лев" -> "лев"
    - punctuation/separators -> spaces
    """
    normalized = unicodedata.normalize("NFKD", str(text or "").lower())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    cleaned_text = re.sub(r"[^\w\s]", " ", without_accents, flags=re.UNICODE)
    cleaned_text = cleaned_text.replace("_", " ")
    return re.sub(r"\s+", " ", cleaned_text).strip()
