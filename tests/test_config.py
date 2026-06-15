from pathlib import Path

from issue_agent.config import AppConfig, RepoConfig, load_config


def test_load_example_config_is_preview_only() -> None:
    config = load_config(Path("examples/config.yaml"))

    assert config.repo == "Kirrito-k423/issue-agent"
    assert config.write_policy == "preview"
    assert config.provider.name == "fixture"
    assert config.label_policy.allowed_labels == ["bug", "question", "enhancement"]


def test_repo_config_splits_owner_and_name() -> None:
    repo = RepoConfig.from_full_name("Kirrito-k423/issue-agent")

    assert repo.owner == "Kirrito-k423"
    assert repo.name == "issue-agent"
    assert repo.full_name == "Kirrito-k423/issue-agent"


def test_app_config_rejects_invalid_repo_name() -> None:
    try:
        AppConfig.model_validate({"repo": "invalid", "state_root": ".issue-agent/state/x"})
    except ValueError as exc:
        assert "repo must use owner/name format" in str(exc)
    else:
        raise AssertionError("invalid repo name was accepted")
