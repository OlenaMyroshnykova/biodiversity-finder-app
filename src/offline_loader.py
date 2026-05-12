"""Utilidades para explicar el modo offline."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OFFLINE_DATA_DIR = PROJECT_ROOT / "data" / "offline"


def is_offline_mode_enabled() -> bool:
    """Devuelve True si OFFLINE_MODE está activado."""
    return os.getenv("OFFLINE_MODE", "false").strip().lower() == "true"


def describe_offline_mode() -> str:
    """Descripción corta del modo offline."""
    if is_offline_mode_enabled():
        return (
            "Modo offline activo: la app intenta usar archivos locales ligeros "
            "antes de consultar Hugging Face."
        )

    return "Modo online: la app descarga artefactos publicados desde Hugging Face."


def expected_offline_files() -> list[Path]:
    """Archivos esperados para trabajar offline."""
    return [
        OFFLINE_DATA_DIR / "species_encyclopedia_light.parquet",
        OFFLINE_DATA_DIR / "species_occurrence_points_light.parquet",
    ]
