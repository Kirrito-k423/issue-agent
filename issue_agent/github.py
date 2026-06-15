import json
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
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


@dataclass(frozen=True)
class GitHubCommandResult:
    command: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""


CommandExecutor = Callable[[Sequence[str]], GitHubCommandResult]


class GitHubMutationRunner:
    def __init__(self, repo: str, executor: CommandExecutor | None = None) -> None:
        self.repo = repo
        self._executor = executor or self._subprocess_executor

    def add_label(self, issue_number: int, label: str) -> GitHubCommandResult:
        return self._run(["gh", "issue", "edit", str(issue_number), "--add-label", label, "--repo", self.repo])

    def remove_label(self, issue_number: int, label: str) -> GitHubCommandResult:
        return self._run(["gh", "issue", "edit", str(issue_number), "--remove-label", label, "--repo", self.repo])

    def post_comment(self, issue_number: int, body: str) -> GitHubCommandResult:
        return self._run(["gh", "issue", "comment", str(issue_number), "--body", body, "--repo", self.repo])

    def close_issue(self, issue_number: int, comment: str | None, reason: str) -> GitHubCommandResult:
        command = ["gh", "issue", "close", str(issue_number)]
        if comment:
            command.extend(["--comment", comment])
        command.extend(["--reason", reason, "--repo", self.repo])
        return self._run(command)

    def _run(self, command: list[str]) -> GitHubCommandResult:
        return self._executor(command)

    @staticmethod
    def _subprocess_executor(command: Sequence[str]) -> GitHubCommandResult:
        completed = subprocess.run(
            list(command),
            capture_output=True,
            check=False,
            text=True,
        )
        return GitHubCommandResult(
            command=list(command),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
