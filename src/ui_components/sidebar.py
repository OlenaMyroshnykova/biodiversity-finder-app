"""Sidebar de búsqueda y filtros."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.offline_loader import describe_offline_mode
from src.ui_components.config import MODEL_DASHBOARD_URL, SEARCH_MODEL_DESCRIPTION
from src.ui_components.language_flags import render_language_block


def render_sidebar_controls(df: pd.DataFrame) -> tuple[str, list[str], int, int, str]:
    """Renderiza controles laterales."""
    render_language_block()

    st.sidebar.header("🔎 Búsqueda Vibe")

    query_text = st.sidebar.text_input(
        "Busca con lenguaje natural",
        placeholder="un bicho pequeño que vive en el desierto",
    )

    selected_classes = st.sidebar.multiselect(
        "Clase taxonómica",
        options=sorted(df["taxon_class"].dropna().unique()) if "taxon_class" in df.columns else [],
        default=[],
    )

    min_observations = st.sidebar.slider(
        "Mínimo de observaciones",
        min_value=1,
        max_value=int(max(1, df["observations"].max())) if "observations" in df.columns else 1,
        value=1,
    )

    max_results = st.sidebar.slider(
        "Número de resultados",
        min_value=5,
        max_value=50,
        value=15,
        step=5,
    )

    selected_species_for_map = ""

    if not df.empty and "scientific_name" in df.columns:
        selected_species_for_map = st.sidebar.selectbox(
            "Especie para mapa Folium",
            options=[""] + sorted(df["scientific_name"].dropna().astype(str).unique().tolist())[:5000],
            index=0,
        )

    st.sidebar.divider()
    st.sidebar.markdown("### 🧠 Buscador")
    st.sidebar.caption(SEARCH_MODEL_DESCRIPTION)
    st.sidebar.caption(describe_offline_mode())

    st.sidebar.link_button(
        "📊 Métricas de adecuación",
        MODEL_DASHBOARD_URL,
        width="stretch",
    )

    st.sidebar.divider()
    st.sidebar.markdown(
        """
        **Ejemplos útiles**

        - `un bicho pequeño que vive en el desierto`
        - `un animal grande de la sabana`
        - `un ave rosa de humedal`
        - `mariposa colorida`
        - `lion`
        - `león`
        - `Panthera leo`
        - `Felidae`
        """
    )

    return query_text, selected_classes, min_observations, max_results, selected_species_for_map
