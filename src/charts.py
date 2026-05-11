"""Gráficos de la aplicación."""

from __future__ import annotations

import altair as alt
import pandas as pd


def build_class_distribution_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Crea gráfico de distribución por clase taxonómica.
    """
    chart_data = (
        df.groupby("taxon_class", as_index=False)
        .agg(observations=("observations", "sum"))
        .sort_values("observations", ascending=False)
        .head(15)
    )

    return (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X("observations:Q", title="Observaciones"),
            y=alt.Y("taxon_class:N", title="Clase", sort="-x"),
            tooltip=["taxon_class", "observations"],
        )
        .properties(height=390, title="Observaciones por clase taxonómica")
    )


def build_map_points_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Crea gráfico de distribución geográfica aproximada.
    """
    chart_data = df.head(500).copy()

    return (
        alt.Chart(chart_data)
        .mark_circle(size=85, opacity=0.68)
        .encode(
            x=alt.X("avg_longitude:Q", title="Longitud media"),
            y=alt.Y("avg_latitude:Q", title="Latitud media"),
            color=alt.Color("taxon_class:N", title="Clase"),
            tooltip=[
                "scientific_name",
                "taxon_class",
                "family",
                "observations",
                "avg_latitude",
                "avg_longitude",
            ],
        )
        .properties(height=390, title="Distribución geográfica aproximada")
    )


def build_search_score_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Muestra ranking de similitud de búsqueda.
    """
    if "search_score" not in df.columns:
        df = df.copy()
        df["search_score"] = 0.0

    chart_data = df.head(15).copy()

    return (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X("search_score:Q", title="Puntuación de búsqueda"),
            y=alt.Y("scientific_name:N", title="Especie", sort="-x"),
            tooltip=[
                "scientific_name",
                "taxon_class",
                "family",
                "search_score",
                "observations",
            ],
        )
        .properties(height=360, title="Ranking de resultados")
    )
