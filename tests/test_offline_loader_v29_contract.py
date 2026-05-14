from pathlib import Path

from src import offline_loader


def test_offline_loader_exports_all_sidebar_helpers() -> None:
    assert offline_loader.ArtifactMode
    assert offline_loader.MODE_LABELS["offline_light"] == "Offline local"
    assert callable(offline_loader.expected_offline_files)
    assert callable(offline_loader.missing_offline_files)
    assert callable(offline_loader.offline_artifacts_available)
    assert callable(offline_loader.has_offline_artifacts)
    assert callable(offline_loader.download_offline_artifacts)
    assert callable(offline_loader.delete_offline_artifacts)


def test_expected_files_accepts_optional_target_dir(tmp_path: Path) -> None:
    expected = offline_loader.expected_offline_files(tmp_path)
    assert {path.name for path in expected} == set(offline_loader.OFFLINE_ARTIFACTS)
    assert all(path.parent == tmp_path for path in expected)
