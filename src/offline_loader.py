"""Offline artifact management for the Streamlit app.

This module keeps the frontend data-mode selector independent from environment
variables and provides small helper functions for downloading/deleting local
light artifacts used by ``Offline local`` mode.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Literal

from huggingface_hub import hf_hub_download

ArtifactMode = Literal["online_full", "online_light", "offline_light"]

REPO_ID = "selenamir/biodiversity-finder-artifacts"
REPO_TYPE = "dataset"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OFFLINE_DATA_DIR = PROJECT_ROOT / "data" / "offline"

# Stable local filenames. Older tests and UI code import this constant directly.
OFFLINE_ARTIFACTS: tuple[str, ...] = (
    "species_encyclopedia_light.parquet",
    "species_occurrence_points_light.parquet",
    "metrics.json",
)

# Remote Hugging Face filenames mapped to the stable local names above.
OFFLINE_REMOTE_FILES: dict[str, str] = {
    "species_encyclopedia_light.parquet": "processed/species_encyclopedia_light.parquet",
    "species_occurrence_points_light.parquet": "processed/species_occurrence_points_light.parquet",
    "metrics.json": "reports/metrics.json",
}

MODE_LABELS: dict[ArtifactMode, str] = {
    "online_full": "Online completo",
    "online_light": "Online ligero",
    "offline_light": "Offline local",
}


def _truthy_env(name: str, default: str = "false") -> bool:
    """Return True for common truthy environment values."""
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def expected_offline_files(target_dir: Path | str | None = None) -> list[Path]:
    """Return local files required for working without network access."""
    base_dir = Path(target_dir) if target_dir is not None else OFFLINE_DATA_DIR
    return [base_dir / filename for filename in OFFLINE_ARTIFACTS]


def missing_offline_files(target_dir: Path | str | None = None) -> list[Path]:
    """Return required offline files that are not present locally."""
    return [path for path in expected_offline_files(target_dir) if not path.exists()]


def has_offline_artifacts(target_dir: Path | str | None = None) -> bool:
    """Return True when all required light artifacts exist locally."""
    return not missing_offline_files(target_dir)


def get_default_artifact_mode() -> ArtifactMode:
    """Return deployment default for the sidebar selector.

    ``OFFLINE_MODE=true`` wins only when local light artifacts are available.
    Otherwise the app starts online and explains what is missing.
    """
    if _truthy_env("OFFLINE_MODE", "false") and has_offline_artifacts():
        return "offline_light"
    if _truthy_env("USE_LIGHT_ARTIFACTS", "false"):
        return "online_light"
    return "online_full"


def describe_artifact_mode(mode: ArtifactMode | str) -> str:
    """Short explanation for the sidebar and the project presentation."""
    if mode == "offline_light":
        if has_offline_artifacts():
            return (
                "Modo offline local: la app lee data/offline/*.parquet y no depende "
                "de Hugging Face para la enciclopedia ni los mapas."
            )
        missing = ", ".join(path.name for path in missing_offline_files())
        return (
            "Modo offline seleccionado, pero faltan archivos locales: "
            f"{missing}. Cambia a modo online o descarga los artifacts offline."
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


def download_offline_artifacts(target_dir: Path | str | None = None) -> list[Path]:
    """Download light artifacts from Hugging Face into ``data/offline``.

    ``target_dir`` is optional for the UI but kept for tests and scripts.
    The function returns the local files that were written.
    """
    base_dir = Path(target_dir) if target_dir is not None else OFFLINE_DATA_DIR
    base_dir.mkdir(parents=True, exist_ok=True)

    token = os.getenv("HF_TOKEN") or None
    downloaded_files: list[Path] = []

    for local_name, remote_name in OFFLINE_REMOTE_FILES.items():
        source_path = Path(
            hf_hub_download(
                repo_id=REPO_ID,
                repo_type=REPO_TYPE,
                filename=remote_name,
                token=token,
            )
        )
        destination_path = base_dir / local_name
        shutil.copyfile(source_path, destination_path)
        downloaded_files.append(destination_path)

    return downloaded_files


def delete_offline_artifacts(target_dir: Path | str | None = None) -> list[Path]:
    """Delete only local offline artifact copies and return deleted paths."""
    deleted_files: list[Path] = []
    for path in expected_offline_files(target_dir):
        if path.exists():
            path.unlink()
            deleted_files.append(path)
    return deleted_files


def offline_artifact_status(target_dir: Path | str | None = None) -> list[dict[str, str | int | bool]]:
    """Return status rows that the sidebar can render without touching HF."""
    rows: list[dict[str, str | int | bool]] = []
    for path in expected_offline_files(target_dir):
        exists = path.exists()
        rows.append(
            {
                "name": path.name,
                "path": str(path),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else 0,
            }
        )
    return rows


# Backwards-compatible helpers used by older tests/code.
def is_offline_mode_enabled() -> bool:
    """Return True only for the legacy environment-based offline mode."""
    return _truthy_env("OFFLINE_MODE", "false")


def describe_offline_mode() -> str:
    """Legacy description used by older UI versions."""
    return describe_artifact_mode(get_default_artifact_mode())
