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
        "Enciclopedia inteligente de biodiversidad basada en datos reales de GBIF. "
        "Puedes buscar en lenguaje natural en español o inglés, o por nombre científico: "
        "`un animal grande de la sabana`, `ave rosa de humedal`, "
        "`jaguar`, `Panthera onca`, `cocodrilo`, `lion`."
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
            + " — el prototipo promete búsqueda estable solo en estos idiomas."
        )

        st.markdown("#### Motor de búsqueda")
        st.write(SEARCH_MODEL_DESCRIPTION)
        st.caption(
            "Los nombres comunes (vernacular names) se obtienen de la API de GBIF "
            "y de Wikidata durante el pipeline de training, y se almacenan en el "
            "campo `vernacular_names` de la enciclopedia. Estos nombres se usan "
            "para las fichas y como búsqueda secundaria por nombre, no para el "
            "vibe-search principal."
        )

        st.markdown("#### Traductor de lenguaje natural")
        st.write(
            "Cuando escribes una frase como 'un bicho pequeño del desierto', "
            "el sistema la traduce automáticamente a máscaras booleanas de Pandas: "
            "`df[(df['size_tag'].str.contains('small')) & "
            "(df['habitat_tag'].str.contains('desert'))]`. "
            "Detecta tamaño, hábitat, color y grupo taxonómico."
        )

        st.markdown("#### Pipeline de datos")
        st.write(
            "El repositorio de training descarga observaciones desde la API de GBIF "
            "para varios grupos taxonómicos. Combina fuentes con `pd.concat()`, "
            "une datos climáticos de NASA POWER con `df.merge()`, enriquece con "
            "nombres comunes vía `df.merge()`, entrena un modelo de clasificación "
            "taxonómica y publica los artefactos en Hugging Face."
        )
        st.link_button("Abrir dashboard de métricas del modelo", MODEL_DASHBOARD_URL)
        st.link_button("Ver dataset y artefactos en Hugging Face", ARTIFACTS_URL)


def render_ethics_notice() -> None:
    """Muestra aviso ético sobre limitaciones de los datos."""
    with st.expander("⚠️ Impacto ético y limitaciones — leer antes de usar", expanded=False):
        st.markdown("#### Sobre los datos")
        st.write(
            "Los datos provienen de GBIF (Global Biodiversity Information Facility), "
            "una plataforma de ciencia ciudadana y registros científicos. "
            "**Los datos de GBIF pueden estar incompletos o sesgados geográficamente**: "
            "las regiones con más acceso tecnológico tienen más registros, "
            "lo que no refleja necesariamente la distribución real de las especies."
        )

        st.markdown("#### Sobre el estado de conservación")
        st.warning(
            "Los estados de conservación mostrados son **estimaciones educativas** "
            "basadas en la rareza de los registros en el dataset, no evaluaciones "
            "oficiales de la UICN (IUCN Red List). "
            "**No uses esta app para tomar decisiones de conservación real.** "
            "Consulta siempre fuentes oficiales como iucnredlist.org."
        )

        st.markdown("#### Sobre las etiquetas de búsqueda")
        st.write(
            "Las etiquetas de color, hábitat y tamaño (`color_tag`, `habitat_tag`, "
            "`size_tag`) son **inferencias automáticas basadas en taxonomía**, "
            "no mediciones biológicas reales. Un arácnido no es necesariamente "
            "pequeño, ni un reptil necesariamente verde. "
            "Tratar estas etiquetas como hechos biológicos sería un error."
        )

        st.markdown("#### Sobre la IA")
        st.write(
            "Esta aplicación es una **herramienta de aprendizaje y exploración**, "
            "no un sistema de identificación de especies. Los resultados dependen "
            "de la calidad del dataset y del modelo de clasificación entrenado con él. "
            "No delegues decisiones críticas — científicas, legales o de conservación — "
            "en los resultados de esta app."
        )

        st.markdown("#### Sobre las especies invasoras")
        st.info(
            "Algunas especies pueden aparecer en países donde no son nativas "
            "debido a registros de especímenes en cautiverio, jardines botánicos "
            "o introducciones accidentales. Los mapas de avistamientos muestran "
            "dónde se han registrado observaciones, no necesariamente el hábitat natural."
        )
