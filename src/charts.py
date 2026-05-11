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
        .head(12)
    )

    return (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusEnd=6)
        .encode(
            x=alt.X("observations:Q", title="Observaciones"),
            y=alt.Y("taxon_class:N", title="Clase", sort="-x"),
            tooltip=["taxon_class", "observations"],
        )
        .properties(height=300, title="Observaciones por clase")
    )


def build_observations_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Muestra las especies con más observaciones.
    """
    chart_data = (
        df.sort_values("observations", ascending=False)
        .head(12)
        .copy()
    )

    return (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusEnd=6)
        .encode(
            x=alt.X("observations:Q", title="Observaciones"),
            y=alt.Y("scientific_name:N", title="Especie", sort="-x"),
            tooltip=["scientific_name", "taxon_class", "family", "observations"],
        )
        .properties(height=300, title="Especies con más observaciones")
    )


def build_map_points_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Crea gráfico de distribución geográfica aproximada.
    """
    chart_data = df.dropna(subset=["avg_longitude", "avg_latitude"]).head(500).copy()

    return (
        alt.Chart(chart_data)
        .mark_circle(size=70, opacity=0.65)
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
        .properties(height=360, title="Distribución geográfica aproximada")
    )


def build_search_score_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Muestra ranking de similitud de búsqueda.
    """
    if "search_score" not in df.columns:
        df = df.copy()
        df["search_score"] = 0.0

    chart_data = df.head(12).copy()

    return (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusEnd=6)
        .encode(
            x=alt.X("search_score:Q", title="Puntuación"),
            y=alt.Y("scientific_name:N", title="Especie", sort="-x"),
            tooltip=[
                "scientific_name",
                "taxon_class",
                "family",
                alt.Tooltip("search_score:Q", format=".3f"),
                "observations",
            ],
        )
        .properties(height=330, title="Ranking de resultados")
    )
