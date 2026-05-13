"""Aplicación Streamlit de Biodiversity Finder."""

from __future__ import annotations

import streamlit as st

from src.artifact_loader import load_encyclopedia, load_metrics, load_occurrence_points
from src.charts import (
    build_class_distribution_chart,
    build_map_points_chart,
    build_search_score_chart,
)
from src.natural_language_query import apply_natural_language_filters
from src.plotly_charts import (
    build_plotly_class_distribution,
    build_plotly_conservation_chart,
    build_plotly_habitat_chart,
)
from src.search import semantic_search_encyclopedia
from src.ui import (
    apply_basic_filters,
    apply_styles,
    render_data_table,
    render_header,
    render_metrics,
    render_sidebar_controls,
    render_species_cards,
)


def main() -> None:
    """Run the Streamlit application."""

    st.set_page_config(
        page_title="Biodiversity Finder",
        page_icon="🌿",
        layout="wide",
    )

    apply_styles()
    render_header()

    encyclopedia_df = load_encyclopedia()
    occurrence_points_df = load_occurrence_points()
    metrics = load_metrics()

    query_text, selected_classes, min_observations, max_results = render_sidebar_controls(
        encyclopedia_df
    )

    filtered_df = apply_basic_filters(
        df=encyclopedia_df,
        selected_classes=selected_classes,
        min_observations=min_observations,
    )

    vibe_filtered_df, parsed_query, nl_fallback = apply_natural_language_filters(
        filtered_df,
        query_text,
    )

    if parsed_query.has_structured_filters:
        if nl_fallback:
            st.warning(
                f"Los filtros detectados (size={parsed_query.size_tags or '-'}, "
                f"habitat={parsed_query.habitat_tags or '-'}, "
                f"color={parsed_query.color_tags or '-'}, "
                f"group={parsed_query.group_tags or '-'}) no encontraron resultados. "
                "Mostrando búsqueda general por nombre/texto."
            )
        else:
            detected = []
            if parsed_query.size_tags:
                detected.append(f"tamaño: {', '.join(parsed_query.size_tags)}")
            if parsed_query.habitat_tags:
                detected.append(f"hábitat: {', '.join(parsed_query.habitat_tags)}")
            if parsed_query.color_tags:
                detected.append(f"color: {', '.join(parsed_query.color_tags)}")
            if parsed_query.group_tags:
                detected.append(f"grupo: {', '.join(parsed_query.group_tags)}")
            st.info(
                "Filtros detectados en tu búsqueda: "
                + " · ".join(detected)
                + ". Aplicando filtros estructurados sobre la enciclopedia."
            )

    result_df = semantic_search_encyclopedia(
        encyclopedia_df=vibe_filtered_df,
        query_text=query_text,
        top_n=max_results,
    )

    render_metrics(result_df, encyclopedia_df, metrics)

    tabs = st.tabs(["Resultados", "Gráficos", "✨ Plotly EDA", "Datos"])

    with tabs[0]:
        st.caption(
            "Cada tarjeta incluye un mapa desplegable con los puntos de avistamiento "
            "registrados en GBIF para esa especie. El estado de conservación procede "
            "de IUCN Red List cuando el token está configurado; si no hay coincidencia, "
            "se muestra 'Sin datos IUCN'."
        )
        render_species_cards(
            result_df,
            query_text=query_text,
            occurrence_points_df=occurrence_points_df,
        )

    with tabs[1]:
        if result_df.empty:
            st.warning("No se encontraron resultados para visualizar.")
        else:
            st.altair_chart(build_class_distribution_chart(result_df), use_container_width=True)
            st.altair_chart(build_search_score_chart(result_df), use_container_width=True)
            st.altair_chart(build_map_points_chart(result_df), use_container_width=True)

    with tabs[2]:
        if result_df.empty:
            st.warning("No se encontraron resultados para visualizar.")
        else:
            st.plotly_chart(build_plotly_class_distribution(result_df), use_container_width=True)
            st.plotly_chart(build_plotly_conservation_chart(result_df), use_container_width=True)
            st.plotly_chart(build_plotly_habitat_chart(result_df), use_container_width=True)

    with tabs[3]:
        render_data_table(result_df)


if __name__ == "__main__":
    main()
