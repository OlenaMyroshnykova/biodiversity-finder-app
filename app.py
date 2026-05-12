"""Aplicación Streamlit de Biodiversity Finder."""

from __future__ import annotations

import streamlit as st

from src.artifact_loader import load_encyclopedia, load_metrics, load_occurrence_points
from src.charts import (
    build_class_distribution_chart,
    build_map_points_chart,
    build_search_score_chart,
)
from src.map_components.species_map import render_results_occurrence_map
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
    """Ejecuta la aplicación."""
    st.set_page_config(
        page_title="Biodiversity Finder",
        page_icon="🐾",
        layout="wide",
    )

    apply_styles()
    render_header()

    encyclopedia_df = load_encyclopedia()
    occurrence_points_df = load_occurrence_points()
    metrics = load_metrics()

    (
        query_text,
        selected_classes,
        min_observations,
        max_results,
        selected_species_for_map,
    ) = render_sidebar_controls(encyclopedia_df)

    filtered_df = apply_basic_filters(
        df=encyclopedia_df,
        selected_classes=selected_classes,
        min_observations=min_observations,
    )

    vibe_filtered_df, parsed_query = apply_natural_language_filters(
        filtered_df,
        query_text,
    )

    if parsed_query.has_structured_filters:
        st.info(
            "🧠 Natural Language to Query detectó filtros: "
            f"size={parsed_query.size_tags or '-'}, "
            f"habitat={parsed_query.habitat_tags or '-'}, "
            f"color={parsed_query.color_tags or '-'}, "
            f"group={parsed_query.group_tags or '-'}"
        )

    result_df = semantic_search_encyclopedia(
        encyclopedia_df=vibe_filtered_df,
        query_text=query_text,
        top_n=max_results,
    )

    render_metrics(result_df, encyclopedia_df, metrics)

    tabs = st.tabs(
        [
            "📚 Resultados",
            "🗺️ Mapa combinado",
            "📊 Gráficos",
            "✨ Plotly EDA",
            "🧾 Datos",
        ]
    )

    with tabs[0]:
        render_species_cards(
            result_df,
            query_text=query_text,
            occurrence_points_df=occurrence_points_df,
        )

    with tabs[1]:
        st.caption(
            "Mapa combinado con coordenadas disponibles para los resultados actuales."
        )

        if selected_species_for_map:
            from src.map_components.species_map import render_species_occurrence_map

            render_species_occurrence_map(
                occurrence_points_df=occurrence_points_df,
                selected_species_name=selected_species_for_map,
                height=520,
                max_points=500,
            )
        else:
            render_results_occurrence_map(
                occurrence_points_df=occurrence_points_df,
                result_df=result_df,
                height=520,
                max_points=500,
            )

    with tabs[2]:
        if result_df.empty:
            st.warning("No se encontraron resultados. Prueba con otra búsqueda o cambia los filtros.")
        else:
            if query_text.strip() and "search_score" in result_df.columns:
                st.altair_chart(build_search_score_chart(result_df), width="stretch")

            chart_column_1, chart_column_2 = st.columns(2)

            with chart_column_1:
                st.altair_chart(build_class_distribution_chart(result_df), width="stretch")

            with chart_column_2:
                st.altair_chart(build_map_points_chart(result_df), width="stretch")

    with tabs[3]:
        if result_df.empty:
            st.warning("No hay datos para graficar.")
        else:
            plotly_chart_1 = build_plotly_class_distribution(result_df)
            plotly_chart_2 = build_plotly_conservation_chart(result_df)
            plotly_chart_3 = build_plotly_habitat_chart(result_df)

            if plotly_chart_1 is not None:
                st.plotly_chart(plotly_chart_1, width="stretch")

            chart_column_1, chart_column_2 = st.columns(2)

            with chart_column_1:
                if plotly_chart_2 is not None:
                    st.plotly_chart(plotly_chart_2, width="stretch")

            with chart_column_2:
                if plotly_chart_3 is not None:
                    st.plotly_chart(plotly_chart_3, width="stretch")

    with tabs[4]:
        render_data_table(result_df)


if __name__ == "__main__":
    main()
