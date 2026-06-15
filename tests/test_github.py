import json
from pathlib import Path

from issue_agent.models import IssueInput, LabelInfo


FIXTURE_PATH = Path("examples/issues.fixture.json")


def test_fixture_issues_validate_into_issue_inputs() -> None:
    raw_issues = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    issues = [IssueInput.model_validate(raw) for raw in raw_issues]

    assert len(issues) >= 2
    assert [issue.number for issue in issues] == [1, 2]
    assert issues[0].comments[0].author == "maintainer-a"


def test_label_info_accepts_optional_description() -> None:
    label = LabelInfo(name="question")

    assert label.name == "question"
    assert label.description is None
