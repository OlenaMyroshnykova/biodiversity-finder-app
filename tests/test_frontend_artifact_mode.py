from src.offline_loader import MODE_LABELS, describe_artifact_mode


def test_frontend_modes_have_user_facing_labels() -> None:
    assert MODE_LABELS["online_full"] == "Online completo"
    assert MODE_LABELS["online_light"] == "Online ligero"
    assert MODE_LABELS["offline_light"] == "Offline local"


def test_offline_mode_description_mentions_local_files() -> None:
    description = describe_artifact_mode("offline_light")
    assert "offline" in description.lower()
    assert "local" in description.lower() or "data/offline" in description.lower()
