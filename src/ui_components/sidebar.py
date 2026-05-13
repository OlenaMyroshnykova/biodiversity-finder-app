"""Sidebar de búsqueda y filtros."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.offline_loader import describe_offline_mode
from src.ui_components.config import MODEL_DASHBOARD_URL, SEARCH_MODEL_DESCRIPTION
from src.ui_components.language_flags import render_language_block
from src.utils.dataframe_filters import get_available_taxon_classes


def render_sidebar_controls(df: pd.DataFrame) -> tuple[str, list[str], int, int]:
    """Renderiza controles laterales basados en el dataset cargado."""

    render_language_block()

    st.sidebar.header("Búsqueda Vibe")

    query_text = st.sidebar.text_input(
        "Busca con lenguaje natural",
        placeholder="un animal grande de la sabana",
    )

    available_classes = get_available_taxon_classes(df)

    selected_classes = st.sidebar.multiselect(
        "Clase taxonómica disponible en el dataset",
        options=available_classes,
        default=[],
        help=(
            "Esta lista se genera automáticamente desde el parquet actual. "
            "La app no usa una lista fija de clases."
        ),
    )

    max_observations = 1
    if "observations" in df.columns and not df.empty:
        max_observations = int(max(1, pd.to_numeric(df["observations"], errors="coerce").fillna(0).max()))

    min_observations = st.sidebar.slider(
        "Mínimo de observaciones",
        min_value=1,
        max_value=max_observations,
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
    st.sidebar.markdown("### Buscador")
    st.sidebar.caption(SEARCH_MODEL_DESCRIPTION)
    st.sidebar.caption(
        "Los mapas están dentro de cada tarjeta de especie, "
        "en la sección desplegable de avistamientos."
    )
    st.sidebar.caption(describe_offline_mode())
    st.sidebar.link_button(
        "Métricas de adecuación",
        MODEL_DASHBOARD_URL,
        width="stretch",
    )

    st.sidebar.divider()
    st.sidebar.markdown(
        """
        **Ejemplos útiles**
        - `un bicho pequeño que vive en el desierto`
        - `un animal grande de la sabana`
        - `un ave de humedal`
        - `animal acuático pequeño`
        - `lion`
        - `león`
        - `Panthera leo`
        """
    )

    return query_text, selected_classes, min_observations, max_results
