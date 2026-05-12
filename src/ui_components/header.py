"""Cabecera de la aplicación."""

from __future__ import annotations

import streamlit as st

from src.ui_components.config import (
    ARTIFACTS_URL,
    MODEL_DASHBOARD_URL,
    SEARCH_MODEL_DESCRIPTION,
    get_supported_languages_text,
)


def render_header() -> None:
    """Renderiza cabecera principal."""
    st.title("🐾 Biodiversity Finder")

    st.info(
        "Enciclopedia inteligente de biodiversidad basada en datos reales de GBIF. "
        "Puedes buscar por nombre común, nombre científico o taxonomía: "
        "`leopardo`, `jaguar`, `frog`, `mariposa`, `Panthera onca`, `Felidae`, "
        "`planta con flor`."
    )

    st.link_button(
        "📊 Ver métricas de adecuación de la modelo",
        MODEL_DASHBOARD_URL,
    )

    render_search_system_info()


def render_search_system_info() -> None:
    """Muestra información sobre búsqueda y modelo."""
    with st.expander("ℹ️ Cómo funciona el buscador", expanded=False):
        st.markdown("#### 🌍 Idiomas")
        st.write(get_supported_languages_text())

        st.markdown("#### 🔎 Buscador")
        st.write(SEARCH_MODEL_DESCRIPTION)
        st.caption(
            "La app ya no contiene reglas específicas para cada animal. "
            "Los nombres comunes vienen del pipeline de training y se guardan "
            "en el campo `vernacular_names`."
        )

        st.markdown("#### 🤖 Pipeline")
        st.write(
            "El repositorio de training descarga datos desde GBIF, combina fuentes con "
            "`pd.concat()`, une datos climáticos con `df.merge()`, une nombres comunes "
            "con otro `df.merge()`, entrena una modelo taxonómica y publica artefactos."
        )

        st.link_button("📊 Abrir dashboard de métricas", MODEL_DASHBOARD_URL)
        st.link_button("📦 Ver dataset y artefactos", ARTIFACTS_URL)
