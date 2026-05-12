"""Sidebar de búsqueda y filtros."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.ui_components.config import MODEL_DASHBOARD_URL, SEARCH_MODEL_DESCRIPTION
from src.ui_components.language_flags import render_language_block


def render_sidebar_controls(df: pd.DataFrame) -> tuple[str, list[str], int, int]:
    """Renderiza controles laterales."""
    render_language_block()

    st.sidebar.header("🔎 Búsqueda")

    query_text = st.sidebar.text_input(
        "Busca con lenguaje natural",
        placeholder="leopardo",
    )

    selected_classes = st.sidebar.multiselect(
        "Clase taxonómica",
        options=sorted(df["taxon_class"].dropna().unique()),
        default=[],
    )

    min_observations = st.sidebar.slider(
        "Mínimo de observaciones",
        min_value=1,
        max_value=int(max(1, df["observations"].max())),
        value=1,
    )

    max_results = st.sidebar.slider(
        "Número de resultados",
        min_value=5,
        max_value=50,
        value=15,
        step=5,
    )

    st.sidebar.divider()
    st.sidebar.markdown("### 🧠 Buscador")
    st.sidebar.caption(SEARCH_MODEL_DESCRIPTION)

    st.sidebar.link_button(
        "📊 Métricas de adecuación",
        MODEL_DASHBOARD_URL,
        width="stretch",
    )

    st.sidebar.divider()
    st.sidebar.markdown(
        """
        **Ejemplos útiles**

        - `leopardo`
        - `jaguar`
        - `Panthera onca`
        - `Felidae`
        - `frog`
        - `mariposa`
        - `planta con flor`
        - `Rosa silvestre`
        """
    )

    return query_text, selected_classes, min_observations, max_results
