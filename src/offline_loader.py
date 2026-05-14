"""Offline artifact utilities for Biodiversity Finder.

This module keeps the frontend/backend contract stable:
- the app can choose between full online, light online, and local offline artifacts;
- the sidebar can download/delete the local light artifact cache;
- tests can monkeypatch ``hf_hub_download`` and pass a custom target directory.
"""

from __future__ import annotations

import os
import shutil
from enum import Enum
from pathlib import Path
from typing import Iterable

from huggingface_hub import hf_hub_download


class ArtifactMode(str, Enum):
    """Data loading modes exposed in the Streamlit sidebar."""

    ONLINE_FULL = "online_full"
    ONLINE_LIGHT = "online_light"
    OFFLINE_LOCAL = "offline_local"


MODE_LABELS: dict[ArtifactMode, str] = {
    ArtifactMode.ONLINE_FULL: "Online completo",
    ArtifactMode.ONLINE_LIGHT: "Online ligero",
    ArtifactMode.OFFLINE_LOCAL: "Offline local",
}

HF_REPO_ID = "selenamir/biodiversity-finder-artifacts"
HF_REPO_TYPE = "dataset"

OFFLINE_DATA_DIR = Path("data/offline")
OFFLINE_ARTIFACTS: tuple[str, ...] = (
    "species_encyclopedia_light.parquet",
    "species_occurrence_points_light.parquet",
    "metrics.json",
)

# Remote locations in the Hugging Face dataset repo. Local filenames stay stable
# and intentionally match OFFLINE_ARTIFACTS.
OFFLINE_REMOTE_FILES: dict[str, str] = {
    "species_encyclopedia_light.parquet": "processed/species_encyclopedia_light.parquet",
    "species_occurrence_points_light.parquet": "processed/species_occurrence_points_light.parquet",
    "metrics.json": "reports/metrics.json",
}


def _resolve_target_dir(target_dir: str | Path | None = None) -> Path:
    return Path(target_dir) if target_dir is not None else OFFLINE_DATA_DIR


def offline_artifact_paths(target_dir: str | Path | None = None) -> dict[str, Path]:
    """Return expected local paths keyed by stable artifact filename."""

    base_dir = _resolve_target_dir(target_dir)
    return {name: base_dir / name for name in OFFLINE_ARTIFACTS}


def missing_offline_artifacts(target_dir: str | Path | None = None) -> list[str]:
    """Return local offline artifact filenames that are not available yet."""

    paths = offline_artifact_paths(target_dir)
    return [name for name, path in paths.items() if not path.exists()]


def offline_artifacts_available(target_dir: str | Path | None = None) -> bool:
    """Compatibility alias expected by older tests and UI code."""

    return not missing_offline_artifacts(target_dir)


def has_offline_artifacts(target_dir: str | Path | None = None) -> bool:
    """Return True when all required local offline artifacts exist."""

    return offline_artifacts_available(target_dir)


def get_missing_offline_artifacts(target_dir: str | Path | None = None) -> list[str]:
    """User-facing alias for missing offline files."""

    return missing_offline_artifacts(target_dir)


def list_offline_artifacts(target_dir: str | Path | None = None) -> list[Path]:
    """List existing local offline artifacts only."""

    return [path for path in offline_artifact_paths(target_dir).values() if path.exists()]


def get_offline_artifact_status(target_dir: str | Path | None = None) -> list[dict[str, object]]:
    """Return lightweight status rows for sidebar display/tests."""

    rows: list[dict[str, object]] = []
    for name, path in offline_artifact_paths(target_dir).items():
        rows.append(
            {
                "name": name,
                "path": str(path),
                "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    return rows


def download_offline_artifacts(target_dir: str | Path | None = None) -> list[Path]:
    """Download light artifacts from Hugging Face into the local offline cache.

    ``target_dir`` is optional so Streamlit can use the default ``data/offline``
    folder, while tests can pass a temporary directory.
    """

    base_dir = _resolve_target_dir(target_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    downloaded: list[Path] = []
    for local_name in OFFLINE_ARTIFACTS:
        remote_name = OFFLINE_REMOTE_FILES[local_name]
        cached_path = Path(
            hf_hub_download(
                repo_id=HF_REPO_ID,
                repo_type=HF_REPO_TYPE,
                filename=remote_name,
            )
        )
        target_path = base_dir / local_name
        shutil.copyfile(cached_path, target_path)
        downloaded.append(target_path)

    return downloaded


def delete_offline_artifacts(target_dir: str | Path | None = None) -> list[Path]:
    """Delete only the local offline copies, never Hugging Face artifacts."""

    deleted: list[Path] = []
    for path in offline_artifact_paths(target_dir).values():
        if path.exists():
            path.unlink()
            deleted.append(path)
    return deleted


def get_default_artifact_mode() -> ArtifactMode:
    """Resolve default mode from environment variables.

    OFFLINE_MODE=true has priority because it is explicit. Otherwise the app
    defaults to the full online artifact unless USE_FULL_ARTIFACTS=false.
    """

    if os.getenv("OFFLINE_MODE", "").strip().lower() in {"1", "true", "yes", "on"}:
        return ArtifactMode.OFFLINE_LOCAL
    if os.getenv("USE_FULL_ARTIFACTS", "true").strip().lower() in {"0", "false", "no", "off"}:
        return ArtifactMode.ONLINE_LIGHT
    return ArtifactMode.ONLINE_FULL


def describe_artifact_mode(mode: ArtifactMode | str) -> str:
    """Return a short Spanish description for the selected data mode."""

    try:
        resolved_mode = ArtifactMode(mode)
    except ValueError:
        resolved_mode = get_default_artifact_mode()

    descriptions = {
        ArtifactMode.ONLINE_FULL: "Usa el artifact completo publicado en Hugging Face.",
        ArtifactMode.ONLINE_LIGHT: "Usa la versión ligera publicada en Hugging Face.",
        ArtifactMode.OFFLINE_LOCAL: "Usa copias locales ligeras guardadas en data/offline/.",
    }
    return descriptions[resolved_mode]
