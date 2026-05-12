"""Renderizado de idiomas."""

from __future__ import annotations

import streamlit as st

from src.ui_components.config import LANGUAGE_FLAGS, get_supported_languages_text


def render_language_flags(compact: bool = True) -> None:
    """Renderiza banderas reales usando st.image."""
    columns = st.columns(len(LANGUAGE_FLAGS))
    width = 30 if compact else 42

    for column, language in zip(columns, LANGUAGE_FLAGS):
        with column:
            st.image(language["image_url"], width=width)


def render_language_block() -> None:
    """Renderiza bloque de idiomas para sidebar."""
    st.sidebar.markdown("### 🌍 Idiomas")
    with st.sidebar:
        render_language_flags(compact=True)
    st.sidebar.caption(get_supported_languages_text())
    st.sidebar.divider()
