"""Language block without flags.

A flag does not represent a language, and the current prototype only promises
stable search in Spanish and English.
"""

from __future__ import annotations

import streamlit as st

from src.ui_components.config import get_supported_languages_text


def render_language_flags(compact: bool = True) -> None:
    """Backward-compatible function: no flags are rendered anymore."""

    render_language_block()


def render_language_block() -> None:
    """Render an honest language-support block in the sidebar."""

    st.sidebar.markdown("### Idiomas de búsqueda")
    st.sidebar.caption(get_supported_languages_text())
    st.sidebar.caption(
        "El vibe-search principal usa vocabulario controlado en español e inglés. "
        "Otros nombres comunes pueden aparecer en fichas, pero no se usan para "
        "decidir filtros estructurados."
    )
    st.sidebar.divider()
