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
    """Render main header."""

    st.title("Biodiversity Finder")
    st.info(
        "Enciclopedia inteligente de biodiversidad basada en datos reales de GBIF, "
        "clima e IUCN Red List cuando el token está configurado. Puedes buscar "
        "en lenguaje natural en español o inglés, o por nombre científico: "
        "`un animal grande de la sabana`, `ave rosa de humedal`, `jaguar`, "
        "`Panthera onca`, `cocodrilo`, `lion`."
    )
    st.link_button("Ver métricas del modelo de clasificación taxonómica", MODEL_DASHBOARD_URL)
    render_search_system_info()
    render_ethics_notice()


def render_search_system_info() -> None:
    """Show search and data-pipeline explanation."""

    with st.expander("ℹ️ Cómo funciona el buscador", expanded=False):
        st.markdown("#### Idiomas soportados")
        st.write(
            get_supported_languages_text()
            + " — el prototipo promete búsqueda estable solo en estos idiomas."
        )

        st.markdown("#### Motor de búsqueda")
        st.write(SEARCH_MODEL_DESCRIPTION)
        st.caption(
            "Los nombres comunes se obtienen durante el pipeline de training y se "
            "usan para fichas y búsqueda secundaria por nombre. No contaminan el "
            "vibe-search principal."
        )

        st.markdown("#### Traductor de lenguaje natural")
        st.write(
            "Cuando escribes una frase como 'un bicho pequeño del desierto', "
            "el sistema la traduce a máscaras booleanas de Pandas: "
            "`df.loc[(df['size_tag'].str.contains('small')) & "
            "(df['habitat_tag'].str.contains('desert'))]`. "
            "Detecta tamaño, hábitat, color y grupo taxonómico."
        )

        st.markdown("#### Pipeline de datos")
        st.write(
            "El repositorio de training descarga observaciones desde GBIF, "
            "combina fuentes con `pd.concat()`, une datos climáticos de NASA POWER "
            "con `df.merge()`, añade nombres comunes/imágenes y une el estado de "
            "conservación de IUCN Red List mediante una tabla cacheada por especie."
        )
        st.link_button("Abrir dashboard de métricas del modelo", MODEL_DASHBOARD_URL)
        st.link_button("Ver dataset y artefactos en Hugging Face", ARTIFACTS_URL)


def render_ethics_notice() -> None:
    """Show ethical limitations of the prototype."""

    with st.expander("⚠️ Impacto ético y limitaciones — leer antes de usar", expanded=False):
        st.markdown("#### Sobre los datos")
        st.write(
            "Los datos provienen de GBIF, una plataforma de ciencia ciudadana y "
            "registros científicos. Pueden estar incompletos o sesgados "
            "geográficamente: las regiones con más acceso tecnológico tienen más "
            "registros, lo que no refleja necesariamente la distribución real de las especies."
        )

        st.markdown("#### Sobre el estado de conservación")
        st.write(
            "Cuando `iucn_is_official` es verdadero, el estado procede de IUCN Red List "
            "o de un campo IUCN oficial de los datos de entrada. Si no hay coincidencia "
            "o no está configurado el token, mostramos `Sin datos IUCN` y no inventamos "
            "una categoría LC como fallback. Consulta siempre iucnredlist.org para "
            "decisiones reales de conservación."
        )

        st.markdown("#### Sobre las etiquetas de búsqueda")
        st.write(
            "Las etiquetas de color, hábitat y tamaño (`color_tag`, `habitat_tag`, "
            "`size_tag`) son inferencias educativas para facilitar el filtrado con Pandas, "
            "no mediciones biológicas oficiales."
        )

        st.markdown("#### Sobre la IA")
        st.write(
            "Esta aplicación es una herramienta de aprendizaje y exploración, no un "
            "sistema de identificación de especies ni una fuente científica final. "
            "No delegues decisiones críticas en los resultados de esta app."
        )

        st.markdown("#### Sobre las especies invasoras")
        st.info(
            "Algunas especies pueden aparecer en países donde no son nativas debido a "
            "registros de especímenes en cautiverio, jardines botánicos o introducciones "
            "accidentales. Los mapas muestran observaciones registradas, no necesariamente "
            "el hábitat natural."
        )
