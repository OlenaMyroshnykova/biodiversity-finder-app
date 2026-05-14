from pathlib import Path

from src import offline_loader


def test_offline_loader_exports_download_contract() -> None:
    assert set(offline_loader.OFFLINE_ARTIFACTS) == {
        "species_encyclopedia_light.parquet",
        "species_occurrence_points_light.parquet",
        "metrics.json",
    }
    assert hasattr(offline_loader, "hf_hub_download")
    assert callable(offline_loader.download_offline_artifacts)
    assert callable(offline_loader.delete_offline_artifacts)


def test_delete_offline_artifacts_only_removes_known_files(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(offline_loader, "OFFLINE_DATA_DIR", tmp_path)
    for name in offline_loader.OFFLINE_ARTIFACTS:
        (tmp_path / name).write_text("fake", encoding="utf-8")
    keep = tmp_path / "do_not_delete.txt"
    keep.write_text("keep", encoding="utf-8")

    removed = offline_loader.delete_offline_artifacts()

    assert {path.name for path in removed} == set(offline_loader.OFFLINE_ARTIFACTS)
    assert keep.exists()
    assert not any((tmp_path / name).exists() for name in offline_loader.OFFLINE_ARTIFACTS)
