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
    st.title("Biodiversity Finder")
    st.info(
        "Enciclopedia visual de biodiversidad basada en observaciones GBIF, "
        "datos climáticos e integración de estado de conservación IUCN cuando "
        "está disponible. Puedes buscar con frases como `un bicho pequeño del "
        "desierto`, `wetland bird`, `cocodrilo` o `Panthera leo`."
    )
    st.link_button(
        "Ver métricas del modelo de clasificación taxonómica",
        MODEL_DASHBOARD_URL,
    )
    render_search_system_info()
    render_ethics_notice()


def render_search_system_info() -> None:
    """Muestra información sobre búsqueda y pipeline."""
    with st.expander("ℹ️ Cómo funciona el buscador", expanded=False):
        st.markdown("#### Idiomas soportados")
        st.write(
            get_supported_languages_text()
            + " — el vibe-search estructurado se mantiene en estos idiomas para que el demo sea estable."
        )
        st.markdown("#### Motor de búsqueda")
        st.write(SEARCH_MODEL_DESCRIPTION)
        st.caption(
            "Los nombres comunes se obtienen en el pipeline de training y se usan "
            "para las fichas y el fallback por nombre, no para contaminar tags_de_busqueda."
        )
        st.markdown("#### Traductor de lenguaje natural")
        st.write(
            "Cuando escribes una frase como 'un bicho pequeño del desierto', "
            "el sistema la traduce a máscaras booleanas de Pandas: "
            "`df.loc[(df['size_tag'].str.contains('small')) & "
            "(df['habitat_tag'].str.contains('desert'))]`."
        )
        st.markdown("#### Pipeline de datos")
        st.write(
            "El repositorio de training descarga observaciones GBIF mediante muestreo "
            "taxonómico neutral, combina fuentes con `pd.concat()`, une datos "
            "climáticos con `pd.merge()`, integra conservación IUCN con `pd.merge()` "
            "y exporta una enciclopedia ligera en Parquet."
        )
        st.link_button("Abrir dashboard de métricas del modelo", MODEL_DASHBOARD_URL)
        st.link_button("Ver dataset y artefactos en Hugging Face", ARTIFACTS_URL)


def render_ethics_notice() -> None:
    """Muestra aviso ético sobre limitaciones de los datos."""
    with st.expander("⚠️ Impacto ético y limitaciones — leer antes de usar", expanded=False):
        st.markdown("#### Sobre los datos")
        st.write(
            "Los datos provienen de GBIF, una plataforma de ciencia ciudadana y "
            "registros científicos. Pueden estar incompletos o sesgados geográficamente."
        )
        st.markdown("#### Sobre el estado de conservación")
        st.write(
            "Cuando el pipeline encuentra una coincidencia oficial, la ficha muestra "
            "`Fuente: IUCN Red List`. Si no hay datos, se muestra `Sin datos IUCN`; "
            "el sistema no inventa categorías como LC."
        )
        st.markdown("#### Sobre las etiquetas de búsqueda")
        st.write(
            "Las etiquetas `color_tag`, `habitat_tag` y `size_tag` son inferencias "
            "educativas para facilitar la búsqueda con Pandas, no mediciones biológicas oficiales."
        )
        st.markdown("#### Sobre especies invasoras")
        st.info(
            "Los mapas muestran dónde se han registrado observaciones, no necesariamente "
            "el hábitat natural ni el área nativa de una especie."
        )
