import json
from pathlib import Path

from issue_agent.models import IssueInput, LabelInfo


def load_fixture_issues(path: Path) -> list[IssueInput]:
    raw_issues = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw_issues, list):
        raise ValueError("fixture issue file must contain a JSON array")
    return [IssueInput.model_validate(raw) for raw in raw_issues]


def load_fixture_labels(config_labels: list[str]) -> list[LabelInfo]:
    return [LabelInfo(name=label) for label in config_labels]


class GitHubClient:
    def __init__(self, repo: str) -> None:
        self.repo = repo

    def list_issues(self) -> list[IssueInput]:
        raise NotImplementedError("live issue listing is not implemented in Phase 1")

    def list_labels(self) -> list[LabelInfo]:
        raise NotImplementedError("live label listing is not implemented in Phase 1")
