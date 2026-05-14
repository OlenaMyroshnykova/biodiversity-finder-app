from pathlib import Path

from src import offline_loader
from src.offline_loader import ArtifactMode


def test_offline_local_mode_keeps_legacy_value() -> None:
    assert ArtifactMode.OFFLINE_LOCAL == "offline_light"
    assert offline_loader.normalize_artifact_mode("offline_local") == ArtifactMode.OFFLINE_LOCAL
    assert offline_loader.normalize_artifact_mode("offline_light") == ArtifactMode.OFFLINE_LOCAL


def test_expected_missing_and_available_contract(tmp_path: Path) -> None:
    expected = offline_loader.expected_offline_files(tmp_path)
    assert {path.name for path in expected} == set(offline_loader.OFFLINE_ARTIFACTS)
    assert not offline_loader.offline_artifacts_available(tmp_path)

    for path in expected:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fake", encoding="utf-8")

    assert offline_loader.offline_artifacts_available(tmp_path)
    assert offline_loader.missing_offline_files(tmp_path) == []
