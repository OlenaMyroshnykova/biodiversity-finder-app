from pathlib import Path

from src import offline_loader


def test_download_offline_artifacts_accepts_optional_target_dir(monkeypatch, tmp_path: Path) -> None:
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
    assert offline_loader.offline_artifacts_available(target_dir)
