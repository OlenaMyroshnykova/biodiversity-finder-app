from pathlib import Path

from src import offline_loader


def test_offline_loader_exports_artifact_mode_contract() -> None:
    assert offline_loader.MODE_LABELS["online_full"] == "Online completo"
    assert offline_loader.MODE_LABELS["online_light"] == "Online ligero"
    assert offline_loader.MODE_LABELS["offline_light"] == "Offline local"
    assert set(offline_loader.OFFLINE_ARTIFACTS) == {
        "species_encyclopedia_light.parquet",
        "species_occurrence_points_light.parquet",
        "metrics.json",
    }


def test_download_offline_artifacts_accepts_target_dir(monkeypatch, tmp_path: Path) -> None:
    fake_cache = tmp_path / "hf-cache"
    fake_cache.mkdir()

    def fake_hf_hub_download(**kwargs):
        source = fake_cache / Path(kwargs["filename"]).name
        source.write_text("fake artifact", encoding="utf-8")
        return str(source)

    monkeypatch.setattr(offline_loader, "hf_hub_download", fake_hf_hub_download)

    target_dir = tmp_path / "offline"
    downloaded = offline_loader.download_offline_artifacts(target_dir)

    assert {path.name for path in downloaded} == set(offline_loader.OFFLINE_ARTIFACTS)
    assert offline_loader.has_offline_artifacts(target_dir)


def test_delete_offline_artifacts_removes_only_expected_files(tmp_path: Path) -> None:
    offline_dir = tmp_path / "offline"
    offline_dir.mkdir()
    keep_file = offline_dir / "README_OFFLINE.md"
    keep_file.write_text("keep", encoding="utf-8")

    for filename in offline_loader.OFFLINE_ARTIFACTS:
        (offline_dir / filename).write_text("artifact", encoding="utf-8")

    deleted = offline_loader.delete_offline_artifacts(offline_dir)

    assert {path.name for path in deleted} == set(offline_loader.OFFLINE_ARTIFACTS)
    assert keep_file.exists()
    assert not offline_loader.has_offline_artifacts(offline_dir)
