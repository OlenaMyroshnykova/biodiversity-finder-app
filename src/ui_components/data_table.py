"""Tabla final de datos."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_data_table(df: pd.DataFrame) -> None:
    """Renderiza tabla compacta final."""
    if df.empty:
        st.info("La tabla está vacía.")
        return

    columns = [
        "scientific_name",
        "vernacular_names",
        "kingdom",
        "taxon_class",
        "taxon_order",
        "family",
        "observations",
        "countries",
        "first_year",
        "last_year",
        "source_queries",
        "avg_latitude",
        "avg_longitude",
    ]

    if "search_score" in df.columns:
        columns = ["search_score"] + columns

    existing_columns = [column for column in columns if column in df.columns]

    st.dataframe(
        df[existing_columns],
        width="stretch",
        hide_index=True,
    )
