"""Utilities for explaining and validating the offline mode.

The Streamlit UI chooses the data mode at runtime. Environment variables remain useful
for deployment defaults, but the frontend selector is the source of truth during a
user session.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

ArtifactMode = Literal["online_full", "online_light", "offline_light"]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OFFLINE_DATA_DIR = PROJECT_ROOT / "data" / "offline"

MODE_LABELS: dict[ArtifactMode, str] = {
    "online_full": "Online completo",
    "online_light": "Online ligero",
    "offline_light": "Offline local",
}


def _truthy_env(name: str, default: str = "false") -> bool:
    """Return True for common truthy environment values."""
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def expected_offline_files() -> list[Path]:
    """Files expected for working without network access."""
    return [
        OFFLINE_DATA_DIR / "species_encyclopedia_light.parquet",
        OFFLINE_DATA_DIR / "species_occurrence_points_light.parquet",
        OFFLINE_DATA_DIR / "metrics.json",
    ]


def has_offline_artifacts() -> bool:
    """Return True when all required light artifacts exist locally."""
    return all(path.exists() for path in expected_offline_files())


def get_default_artifact_mode() -> ArtifactMode:
    """Deployment default for the sidebar selector.

    OFFLINE_MODE=true wins only when local light artifacts are available. Otherwise the
    app starts in online mode and explains what is missing.
    """
    if _truthy_env("OFFLINE_MODE", "false") and has_offline_artifacts():
        return "offline_light"
    if _truthy_env("USE_LIGHT_ARTIFACTS", "false"):
        return "online_light"
    return "online_full"


def describe_artifact_mode(mode: ArtifactMode | str) -> str:
    """Short text for the sidebar and the presentation/demo."""
    if mode == "offline_light":
        if has_offline_artifacts():
            return (
                "Modo offline local: la app lee data/offline/*.parquet y no depende "
                "de Hugging Face para la enciclopedia ni los mapas."
            )
        missing = [path.name for path in expected_offline_files() if not path.exists()]
        return (
            "Modo offline solicitado, pero faltan archivos locales: "
            + ", ".join(missing)
            + ". Ejecuta: python scripts/download_offline_artifacts.py"
        )
    if mode == "online_light":
        return (
            "Modo online ligero: descarga los artifacts light desde Hugging Face. "
            "Sirve para demo rápida o conexiones lentas."
        )
    return (
        "Modo online completo: descarga el artifact completo desde Hugging Face. "
        "Es el modo recomendado para máxima cobertura de búsqueda."
    )


# Backwards-compatible helpers used by older tests/code.
def is_offline_mode_enabled() -> bool:
    """Return True only for the legacy environment-based offline mode."""
    return _truthy_env("OFFLINE_MODE", "false")


def describe_offline_mode() -> str:
    """Legacy description used by older UI versions."""
    return describe_artifact_mode(get_default_artifact_mode())
