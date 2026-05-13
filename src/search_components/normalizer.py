"""Text normalization for the demo search.

Keeps Unicode letters so exact fallback search still works when common names in
artifacts contain non-Latin text. The UI only promises Spanish + English for
vibe search, but fallback name search should not destroy names already present
in the dataset.
"""
from __future__ import annotations

import re
import unicodedata


def normalize_text(text: object) -> str:
    """Normalize text to lowercase tokens while preserving Unicode letters."""
    normalized = unicodedata.normalize("NFKD", str(text or "").lower())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    cleaned_text = re.sub(r"[^\w\s]", " ", without_accents, flags=re.UNICODE)
    return re.sub(r"\s+", " ", cleaned_text).strip()
