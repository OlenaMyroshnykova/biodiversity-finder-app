"""Normalización de texto para búsqueda en español e inglés.

Conserva letras latinas y números. El soporte cirílico se retira del flujo de
búsqueda principal porque la UI ya no promete ruso/ucraniano.
"""

from __future__ import annotations

import re
import unicodedata


def normalize_text(text: object) -> str:
    """Normaliza texto para vocabulario controlado ES/EN."""
    normalized = unicodedata.normalize("NFKD", str(text).lower())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    cleaned_text = re.sub(r"[^a-z0-9ñç\s]", " ", without_accents)
    return re.sub(r"\s+", " ", cleaned_text).strip()
