"""Métricas principales de la app."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_metrics(result_df: pd.DataFrame, full_df: pd.DataFrame, metrics: dict) -> None:
    """Muestra métricas principales."""
    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:
        st.metric("Resultados", f"{len(result_df):,}")

    with column_2:
        observations = int(result_df["observations"].sum()) if not result_df.empty else 0
        st.metric("Observaciones filtradas", f"{observations:,}")

    with column_3:
        st.metric("Especies en dataset", f"{len(full_df):,}")

    with column_4:
        accuracy = metrics.get("accuracy")
        accuracy_text = f"{accuracy * 100:.1f}%" if isinstance(accuracy, (int, float)) else "N/A"
        st.metric("Accuracy ML", accuracy_text)
