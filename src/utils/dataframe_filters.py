"""Helpers para filtrar dataframes de la app."""
from __future__ import annotations

import pandas as pd

PROJECT_SCOPE_KINGDOMS = {"Animalia", "Plantae"}


def filter_project_scope(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve solo Animalia + Plantae cuando la columna kingdom existe."""
    if df.empty or "kingdom" not in df.columns:
        return df.copy()
    scoped = df[df["kingdom"].fillna("").astype(str).isin(PROJECT_SCOPE_KINGDOMS)].copy()
    return scoped if not scoped.empty else df.copy()


def get_available_taxon_classes(df: pd.DataFrame) -> list[str]:
    """Obtiene clases taxonómicas disponibles directamente desde el dataset."""
    if df.empty or "taxon_class" not in df.columns:
        return []
    scoped = filter_project_scope(df)
    classes = (
        scoped["taxon_class"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    return sorted(value for value in classes.unique().tolist() if value)


def apply_taxon_class_filter(df: pd.DataFrame, selected_class: str | None) -> pd.DataFrame:
    """Filtra por clase taxonómica si se ha seleccionado una clase concreta."""
    if not selected_class or selected_class == "Todas" or "taxon_class" not in df.columns:
        return df.copy()
    return df[df["taxon_class"].fillna("").astype(str).eq(selected_class)].copy()
