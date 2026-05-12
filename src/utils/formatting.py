"""Formateo seguro de valores."""

from __future__ import annotations

import pandas as pd


def format_coordinate(value: object) -> str:
    """Formatea coordenadas de forma segura."""
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "N/A"


def format_integer(value: object) -> str:
    """Formatea enteros de forma segura."""
    try:
        if pd.isna(value):
            return "0"
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def format_score(value: object) -> str:
    """Formatea score de búsqueda de forma segura."""
    try:
        if pd.isna(value):
            return "0.000"
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "0.000"
