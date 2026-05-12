"""Gráficos Plotly para EDA visual en la app."""

from __future__ import annotations

import pandas as pd


def build_plotly_class_distribution(df: pd.DataFrame):
    """Distribución de resultados por clase taxonómica."""
    import plotly.express as px

    if df.empty or "taxon_class" not in df.columns:
        return None

    chart_df = (
        df.groupby("taxon_class", as_index=False)
        .agg(species_count=("scientific_name", "nunique"))
        .sort_values("species_count", ascending=False)
    )

    return px.bar(
        chart_df,
        x="taxon_class",
        y="species_count",
        title="Distribución por clase taxonómica",
        labels={
            "taxon_class": "Clase",
            "species_count": "Número de especies",
        },
    )


def build_plotly_conservation_chart(df: pd.DataFrame):
    """Resumen de conservación."""
    import plotly.express as px

    if df.empty or "conservation_status" not in df.columns:
        return None

    chart_df = (
        df.groupby("conservation_status", as_index=False)
        .agg(species_count=("scientific_name", "nunique"))
        .sort_values("species_count", ascending=False)
    )

    return px.pie(
        chart_df,
        names="conservation_status",
        values="species_count",
        title="Estatus de conservación en los resultados",
    )


def build_plotly_habitat_chart(df: pd.DataFrame):
    """Resumen por habitat_tag."""
    import plotly.express as px

    if df.empty or "habitat_tag" not in df.columns:
        return None

    chart_df = (
        df.groupby("habitat_tag", as_index=False)
        .agg(species_count=("scientific_name", "nunique"))
        .sort_values("species_count", ascending=False)
        .head(12)
    )

    return px.bar(
        chart_df,
        x="species_count",
        y="habitat_tag",
        orientation="h",
        title="Hábitats detectados por tags",
        labels={
            "species_count": "Número de especies",
            "habitat_tag": "Hábitat",
        },
    )
