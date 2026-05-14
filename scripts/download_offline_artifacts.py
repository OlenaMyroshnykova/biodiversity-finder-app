"""Download light artifacts for offline demos.

Run from the repository root:

    python scripts/download_offline_artifacts.py

The files are saved into data/offline/, which is the path used by the
Streamlit "Offline local" mode.
"""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.offline_loader import OFFLINE_DATA_DIR, download_offline_artifacts


def main() -> None:
    downloaded_paths = download_offline_artifacts(OFFLINE_DATA_DIR)
    print("Artifacts offline descargados en:")
    print(OFFLINE_DATA_DIR)
    for path in downloaded_paths:
        print(f"- {path.name}")


if __name__ == "__main__":
    main()
