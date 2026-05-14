"""Offline artifact management for the Streamlit app.

Architecture:
- Training publishes light artifacts to Hugging Face.
- The app can download those light artifacts into ``data/offline``.
- Offline mode reads only local files from ``data/offline``.

This module intentionally keeps backwards-compatible helper names because several
UI modules and tests import them directly.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Literal

from huggingface_hub import hf_hub_download

ArtifactMode = Literal["online_full", "online_light", "offline_light"]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OFFLINE_DATA_DIR = PROJECT_ROOT / "data" / "offline"

HF_REPO_ID = "selenamir/biodiversity-finder-artifacts"
HF_REPO_TYPE = "dataset"

MODE_LABELS: dict[ArtifactMode, str] = {
    "online_full": "Online completo",
    "online_light": "Online ligero",
    "offline_light": "Offline local",
}

# Stable local filenames expected by tests, scripts and sidebar UI.
OFFLINE_ARTIFACTS: tuple[str, str, str] = (
    "species_encyclopedia_light.parquet",
    "species_occurrence_points_light.parquet",
    "metrics.json",
)

# Hugging Face paths -> local data/offline filenames.
OFFLINE_ARTIFACT_SOURCES: dict[str, str] = {
    "processed/species_encyclopedia_light.parquet": "species_encyclopedia_light.parquet",
    "processed/species_occurrence_points_light.parquet": "species_occurrence_points_light.parquet",
    "reports/metrics.json": "metrics.json",
}


def _truthy_env(name: str, default: str = "false") -> bool:
    """Return True for common truthy environment values."""
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def _resolve_target_dir(target_dir: str | Path | None = None) -> Path:
    """Return the offline artifact directory, creating it when needed."""
    directory = Path(target_dir) if target_dir is not None else OFFLINE_DATA_DIR
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def expected_offline_files(target_dir: str | Path | None = None) -> list[Path]:
    """Files expected for working without network access.

    ``target_dir`` is optional for testability; in the real app it defaults to
    ``data/offline`` inside the repository.
    """
    directory = Path(target_dir) if target_dir is not None else OFFLINE_DATA_DIR
    return [directory / filename for filename in OFFLINE_ARTIFACTS]


def missing_offline_files(target_dir: str | Path | None = None) -> list[Path]:
    """Return local offline artifacts that are still missing."""
    return [path for path in expected_offline_files(target_dir) if not path.exists()]


def offline_artifacts_available(target_dir: str | Path | None = None) -> bool:
    """Return True when all required local light artifacts are available."""
    return not missing_offline_files(target_dir)


def has_offline_artifacts(target_dir: str | Path | None = None) -> bool:
    """Alias used by newer UI code."""
    return offline_artifacts_available(target_dir)


def download_offline_artifacts(target_dir: str | Path | None = None) -> list[Path]:
    """Download light artifacts from Hugging Face into the local offline folder.

    Returns the paths written locally. The optional target directory keeps older
    tests and command-line scripts simple.
    """
    directory = _resolve_target_dir(target_dir)
    token = os.getenv("HF_TOKEN") or None
    written_paths: list[Path] = []

    for hf_filename, local_filename in OFFLINE_ARTIFACT_SOURCES.items():
        cached_path = Path(
            hf_hub_download(
                repo_id=HF_REPO_ID,
                repo_type=HF_REPO_TYPE,
                filename=hf_filename,
                token=token,
            )
        )
        target_path = directory / local_filename
        shutil.copy2(cached_path, target_path)
        written_paths.append(target_path)

    return written_paths


def delete_offline_artifacts(target_dir: str | Path | None = None) -> list[Path]:
    """Delete only local offline artifact files and return deleted paths."""
    deleted_paths: list[Path] = []
    for path in expected_offline_files(target_dir):
        if path.exists() and path.is_file():
            path.unlink()
            deleted_paths.append(path)
    return deleted_paths


def get_default_artifact_mode() -> ArtifactMode:
    """Deployment default for the sidebar selector.

    ``OFFLINE_MODE=true`` wins only when local light artifacts are available.
    Otherwise the app starts in online mode and explains what is missing.
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
        missing = [path.name for path in missing_offline_files()]
        return (
            "Modo offline solicitado, pero faltan archivos locales: "
            + ", ".join(missing)
            + ". Puedes descargarlos desde la barra lateral."
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
