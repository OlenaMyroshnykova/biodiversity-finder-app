"""Métricas principales de la app."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def _count_official_iucn(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    if "conservation_source" in df.columns:
        return int(df["conservation_source"].fillna("").astype(str).eq("IUCN Red List").sum())
    if "iucn_is_official" in df.columns:
        return int(df["iucn_is_official"].fillna(False).astype(bool).sum())
    return 0


def render_metrics(result_df: pd.DataFrame, full_df: pd.DataFrame, metrics: dict) -> None:
    """Muestra métricas principales."""
    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:
        st.metric("Resultados", f"{len(result_df):,}")

    with column_2:
        observations = int(result_df["observations"].sum()) if "observations" in result_df.columns and not result_df.empty else 0
        st.metric("Observaciones filtradas", f"{observations:,}")

    with column_3:
        st.metric("Especies en dataset", f"{len(full_df):,}")

    with column_4:
        st.metric("Estados IUCN oficiales", f"{_count_official_iucn(full_df):,}")
        accuracy = metrics.get("accuracy")
        if isinstance(accuracy, (int, float)):
            st.caption(f"Modelo taxonómico demo: {accuracy * 100:.1f}% accuracy")
        else:
            st.caption("Modelo taxonómico demo")
