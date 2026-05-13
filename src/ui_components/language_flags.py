"""Bloque informativo de idiomas sin banderas.

No usamos banderas porque una bandera no representa un idioma y porque el
prototipo actual solo promete búsqueda estable en español e inglés.
"""

from __future__ import annotations

import streamlit as st

from src.ui_components.config import get_supported_languages_text


def render_language_flags(compact: bool = True) -> None:
    """Compatibilidad con imports antiguos: ya no renderiza banderas."""
    render_language_block()


def render_language_block() -> None:
    """Renderiza un bloque honesto sobre idiomas soportados."""
    st.sidebar.markdown("### Idiomas de búsqueda")
    st.sidebar.caption(get_supported_languages_text())
    st.sidebar.caption(
        "El vibe-search principal usa vocabulario controlado en español e inglés. "
        "Los nombres comunes de otros idiomas pueden aparecer en las fichas, "
        "pero no se usan para decidir los filtros estructurados."
    )
    st.sidebar.divider()
