"""Aplicación Streamlit de Biodiversity Finder."""

from __future__ import annotations

import streamlit as st

from src.artifact_loader import load_encyclopedia, load_metrics
from src.charts import (
    build_class_distribution_chart,
    build_map_points_chart,
    build_observations_chart,
    build_search_score_chart,
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
    """Ejecuta la aplicación online."""
    st.set_page_config(
        page_title="Biodiversity Finder",
        page_icon="🐾",
        layout="wide",
    )

    apply_styles()
    render_header()

    encyclopedia_df = load_encyclopedia()
    metrics = load_metrics()

    query_text, selected_classes, min_observations, max_results = render_sidebar_controls(
        encyclopedia_df
    )

    filtered_df = apply_basic_filters(
        df=encyclopedia_df,
        selected_classes=selected_classes,
        min_observations=min_observations,
    )

    result_df = semantic_search_encyclopedia(
        encyclopedia_df=filtered_df,
        query_text=query_text,
        top_n=max_results,
    )

    render_metrics(result_df, encyclopedia_df, metrics)

    results_tab, charts_tab, data_tab = st.tabs(
        ["📚 Resultados", "📊 Gráficos", "🧾 Datos"]
    )

    with results_tab:
        render_species_cards(result_df, query_text=query_text)

    with charts_tab:
        if result_df.empty:
            st.warning("No hay datos suficientes para construir gráficos.")
        else:
            st.subheader("Ranking de búsqueda")
            if query_text.strip():
                st.altair_chart(build_search_score_chart(result_df), width="stretch")
            else:
                st.info("Escribe una búsqueda para ver el ranking de similitud.")

            chart_column_1, chart_column_2 = st.columns(2)

            with chart_column_1:
                st.altair_chart(
                    build_class_distribution_chart(result_df),
                    width="stretch",
                )

            with chart_column_2:
                st.altair_chart(
                    build_observations_chart(result_df),
                    width="stretch",
                )

            st.altair_chart(
                build_map_points_chart(result_df),
                width="stretch",
            )

    with data_tab:
        render_data_table(result_df)


if __name__ == "__main__":
    main()
