import json
from pathlib import Path

from issue_agent.github import GitHubClient, load_fixture_issues, load_fixture_labels
from issue_agent.models import IssueInput, LabelInfo


FIXTURE_PATH = Path("examples/issues.fixture.json")


def test_fixture_issues_validate_into_issue_inputs() -> None:
    raw_issues = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    issues = [IssueInput.model_validate(raw) for raw in raw_issues]

    assert len(issues) >= 4
    assert [issue.number for issue in issues] == [1, 2, 3, 4]
    assert issues[0].comments[0].author == "maintainer-a"


def test_label_info_accepts_optional_description() -> None:
    label = LabelInfo(name="question")

    assert label.name == "question"
    assert label.description is None


def test_fixture_issue_loader_preserves_order() -> None:
    issues = load_fixture_issues(FIXTURE_PATH)

    assert [issue.number for issue in issues] == [1, 2, 3, 4]
    assert issues[0].labels == ["question"]


def test_fixture_label_loader_uses_config_order() -> None:
    labels = load_fixture_labels(["bug", "question", "enhancement"])

    assert [label.name for label in labels] == ["bug", "question", "enhancement"]


def test_github_client_is_read_only_shape() -> None:
    client = GitHubClient("Kirrito-k423/issue-agent")

    assert client.repo == "Kirrito-k423/issue-agent"
    assert callable(client.list_issues)
    assert callable(client.list_labels)
