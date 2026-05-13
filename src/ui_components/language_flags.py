"""Bloque de idiomas sin banderas.

Una bandera no representa un idioma y el prototipo no debe prometer más
idiomas de los que soporta de forma estable.
"""
from __future__ import annotations

import streamlit as st

from src.ui_components.config import get_supported_languages_text


def render_language_flags(compact: bool = True) -> None:
    """Compatibilidad: ya no renderiza banderas."""
    st.caption(f"Búsqueda disponible en: {get_supported_languages_text()}.")


def render_language_block() -> None:
    """Renderiza bloque honesto de idiomas para sidebar."""
    st.sidebar.markdown("### Idiomas de búsqueda")
    st.sidebar.caption(f"Búsqueda estable en {get_supported_languages_text()}.")
    st.sidebar.caption("Los nombres comunes de otros idiomas pueden aparecer en fichas, pero no controlan el vibe-search.")
    st.sidebar.divider()
