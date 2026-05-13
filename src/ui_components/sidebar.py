"""Sidebar de búsqueda y filtros."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.offline_loader import describe_offline_mode
from src.ui_components.config import MODEL_DASHBOARD_URL, SEARCH_MODEL_DESCRIPTION
from src.ui_components.language_flags import render_language_block


def render_sidebar_controls(df: pd.DataFrame) -> tuple[str, list[str], int, int]:
    """Renderiza controles laterales."""
    render_language_block()

    st.sidebar.header("🔎 Búsqueda")

    query_text = st.sidebar.text_input(
        "Busca en lenguaje natural o por nombre científico",
        placeholder="un bicho pequeño que vive en el desierto",
    )

    selected_classes = st.sidebar.multiselect(
        "Filtrar por clase taxonómica",
        options=sorted(df["taxon_class"].dropna().unique()) if "taxon_class" in df.columns else [],
        default=[],
    )

    min_observations = st.sidebar.slider(
        "Mínimo de observaciones en el dataset",
        min_value=1,
        max_value=int(max(1, df["observations"].max())) if "observations" in df.columns else 1,
        value=1,
    )

    max_results = st.sidebar.slider(
        "Número máximo de resultados",
        min_value=5,
        max_value=50,
        value=15,
        step=5,
    )

    st.sidebar.divider()
    st.sidebar.markdown("### 🔍 Motor de búsqueda")
    st.sidebar.caption(SEARCH_MODEL_DESCRIPTION)
    st.sidebar.caption(
        "Los mapas están dentro de cada tarjeta de especie (sección desplegable 🗺️). "
    )
    st.sidebar.caption(describe_offline_mode())

    st.sidebar.link_button(
        "📊 Métricas del clasificador taxonómico",
        MODEL_DASHBOARD_URL,
        width="stretch",
    )

    st.sidebar.divider()
    st.sidebar.markdown("**Ejemplos de búsqueda**")
    st.sidebar.markdown(
        """
        - `un bicho pequeño del desierto`
        - `ave rosa de humedal`
        - `animal grande de la sabana`
        - `cocodrilo` / `crocodile` / `крокодил`
        - `tiburón` / `shark` / `акула`
        - `hongo` / `mushroom` / `гриб`
        - `araña` / `spider` / `паук`
        - `lion` / `león` / `Panthera leo`
        - `mariposa colorida`
        - `Felidae` / `Amphibia`
        """
    )

    return query_text, selected_classes, min_observations, max_results
