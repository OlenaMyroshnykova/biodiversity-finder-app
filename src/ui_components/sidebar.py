"""Sidebar controls for the Streamlit app."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.offline_loader import describe_offline_mode
from src.ui_components.config import MODEL_DASHBOARD_URL, SEARCH_MODEL_DESCRIPTION
from src.utils.dataframe_filters import get_available_taxon_classes


def render_sidebar_controls(df: pd.DataFrame) -> tuple[str, list[str], int, int]:
    """Render sidebar controls for the single-box vibe search."""
    st.sidebar.header("Búsqueda")
    st.sidebar.caption("Búsqueda principal disponible en Español e Inglés.")

    query_text = st.sidebar.text_input(
        "Busca en lenguaje natural o por nombre científico",
        placeholder="un bicho pequeño que vive en el desierto",
    )

    available_classes = get_available_taxon_classes(df)
    selected_classes = st.sidebar.multiselect(
        "Filtrar por clase taxonómica disponible en el dataset",
        options=available_classes,
        default=[],
    )

    if "observations" in df.columns and not df.empty:
        max_observations = int(max(1, pd.to_numeric(df["observations"], errors="coerce").fillna(0).max()))
    else:
        max_observations = 1

    min_observations = st.sidebar.slider(
        "Mínimo de observaciones en el dataset",
        min_value=1,
        max_value=max_observations,
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
    st.sidebar.markdown("### Motor de búsqueda")
    st.sidebar.caption(SEARCH_MODEL_DESCRIPTION)
    st.sidebar.caption("Los mapas están dentro de cada tarjeta de especie, en una sección desplegable.")
    st.sidebar.caption(describe_offline_mode())
    st.sidebar.link_button(
        "Métricas del clasificador taxonómico",
        MODEL_DASHBOARD_URL,
        width="stretch",
    )

    st.sidebar.divider()
    st.sidebar.markdown("**Ejemplos de búsqueda**")
    st.sidebar.markdown(
        """
        - `un bicho pequeño del desierto`
        - `ave de humedal`
        - `animal grande de la sabana`
        - `cocodrilo` / `crocodile`
        - `tiburón` / `shark`
        - `araña` / `spider`
        - `lion` / `león` / `Panthera leo`
        - `Felidae` / `Amphibia`
        """
    )

    return query_text, selected_classes, min_observations, max_results
