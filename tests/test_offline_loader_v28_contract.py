from pathlib import Path

from src import offline_loader


def test_offline_artifacts_available_alias_accepts_target_dir(tmp_path: Path) -> None:
    assert not offline_loader.offline_artifacts_available(tmp_path)
    for name in offline_loader.OFFLINE_ARTIFACTS:
        (tmp_path / name).write_text("fake", encoding="utf-8")
    assert offline_loader.offline_artifacts_available(tmp_path)
    assert offline_loader.has_offline_artifacts(tmp_path)


def test_delete_offline_artifacts_removes_only_expected_files(tmp_path: Path) -> None:
    expected = []
    for name in offline_loader.OFFLINE_ARTIFACTS:
        path = tmp_path / name
        path.write_text("fake", encoding="utf-8")
        expected.append(path)
    keep = tmp_path / "README_OFFLINE.md"
    keep.write_text("keep", encoding="utf-8")

    deleted = offline_loader.delete_offline_artifacts(tmp_path)

    assert set(deleted) == set(expected)
    assert keep.exists()
    assert not offline_loader.offline_artifacts_available(tmp_path)
