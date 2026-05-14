"""Helpers for app data modes and local offline artifacts.

The app can run in three modes:
- online_full: full Hugging Face artifacts
- online_light: light Hugging Face artifacts
- offline_light: local light artifacts stored in data/offline/

This module is intentionally small and stable because both the Streamlit UI and
contract tests rely on these names.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from huggingface_hub import hf_hub_download

ArtifactMode = Literal["online_full", "online_light", "offline_light"]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OFFLINE_DATA_DIR = PROJECT_ROOT / "data" / "offline"

HF_REPO_ID = os.getenv("HF_ARTIFACT_REPO_ID", "selenamir/biodiversity-finder-artifacts")
HF_REPO_TYPE = "dataset"

# Stable local filenames expected by tests, UI and the artifact loader.
OFFLINE_ARTIFACTS: tuple[str, ...] = (
    "species_encyclopedia_light.parquet",
    "species_occurrence_points_light.parquet",
    "metrics.json",
)

# Remote Hugging Face path -> local stable filename.
OFFLINE_ARTIFACT_MAP: dict[str, str] = {
    "processed/species_encyclopedia_light.parquet": "species_encyclopedia_light.parquet",
    "processed/species_occurrence_points_light.parquet": "species_occurrence_points_light.parquet",
    "reports/metrics.json": "metrics.json",
}

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
    return [OFFLINE_DATA_DIR / filename for filename in OFFLINE_ARTIFACTS]


def missing_offline_files() -> list[Path]:
    """Return the offline files that are still missing locally."""
    return [path for path in expected_offline_files() if not path.exists()]


def has_offline_artifacts() -> bool:
    """Return True when all required light artifacts exist locally."""
    return not missing_offline_files()


def download_offline_artifacts() -> list[Path]:
    """Download light artifacts from Hugging Face into data/offline/.

    The fixed local folder is intentional: after the download, Offline local can
    reliably load the files without asking the user for a path. Keeping
    hf_hub_download imported at module level also makes this function easy to
    monkeypatch in tests.
    """
    OFFLINE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    token = os.getenv("HF_TOKEN") or None
    saved_paths: list[Path] = []

    for remote_filename, local_name in OFFLINE_ARTIFACT_MAP.items():
        cached_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            repo_type=HF_REPO_TYPE,
            filename=remote_filename,
            token=token,
        )
        target_path = OFFLINE_DATA_DIR / local_name
        target_path.write_bytes(Path(cached_path).read_bytes())
        saved_paths.append(target_path)

    return saved_paths


def delete_offline_artifacts() -> list[Path]:
    """Delete only the known local offline artifacts from data/offline/."""
    removed: list[Path] = []
    for path in expected_offline_files():
        if path.exists():
            path.unlink()
            removed.append(path)
    return removed


def get_default_artifact_mode() -> ArtifactMode:
    """Deployment default for the sidebar selector."""
    if _truthy_env("OFFLINE_MODE", "false") and has_offline_artifacts():
        return "offline_light"
    if _truthy_env("USE_LIGHT_ARTIFACTS", "false"):
        return "online_light"
    return "online_full"


def describe_artifact_mode(mode: ArtifactMode | str) -> str:
    """Short text for the sidebar and demo."""
    if mode == "offline_light":
        if has_offline_artifacts():
            return (
                "Modo offline local: la app lee data/offline/*.parquet y no depende "
                "de Hugging Face para la enciclopedia ni los mapas."
            )
        missing = ", ".join(path.name for path in missing_offline_files())
        return (
            "Modo offline solicitado, pero faltan archivos locales: "
            f"{missing}. Puedes descargarlos desde el botón del panel lateral."
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
