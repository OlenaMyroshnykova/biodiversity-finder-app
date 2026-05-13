"""Optional Plotly charts for the app."""
from __future__ import annotations

import pandas as pd


def _get_plotly_express():
    try:
        import plotly.express as px
        return px
    except ModuleNotFoundError:
        return None


def build_plotly_class_distribution(df: pd.DataFrame):
    """Distribution of results by taxonomic class."""
    px = _get_plotly_express()
    if px is None or df.empty or "taxon_class" not in df.columns:
        return None
    chart_df = df["taxon_class"].fillna("Unknown").value_counts().reset_index()
    chart_df.columns = ["taxon_class", "species_count"]
    return px.bar(chart_df, x="taxon_class", y="species_count", title="Distribución por clase")


def build_plotly_conservation_chart(df: pd.DataFrame):
    """Distribution by IUCN category."""
    px = _get_plotly_express()
    if px is None or df.empty:
        return None
    column = "iucn_category" if "iucn_category" in df.columns else "conservation_status"
    if column not in df.columns:
        return None
    chart_df = df[column].fillna("NO_DATA").value_counts().reset_index()
    chart_df.columns = [column, "species_count"]
    return px.bar(chart_df, x=column, y="species_count", title="Estado de conservación")


def build_plotly_habitat_chart(df: pd.DataFrame):
    """Distribution by habitat tag."""
    px = _get_plotly_express()
    if px is None or df.empty or "habitat_tag" not in df.columns:
        return None
    chart_df = df["habitat_tag"].fillna("Unknown").value_counts().reset_index()
    chart_df.columns = ["habitat_tag", "species_count"]
    return px.bar(chart_df, x="habitat_tag", y="species_count", title="Hábitat tag")
