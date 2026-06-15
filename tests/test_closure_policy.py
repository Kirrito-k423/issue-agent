from pathlib import Path

from issue_agent.github import load_fixture_issues
from issue_agent.links import extract_linked_references
from issue_agent.models import IssueComment, IssueInput
from issue_agent.policy import evaluate_closure_policy


FIXTURE_PATH = Path("examples/issues.fixture.json")
REPO = "Kirrito-k423/issue-agent"


def test_help_wanted_issue_with_linked_pr_is_not_suitable_to_close() -> None:
    issue = next(issue for issue in load_fixture_issues(FIXTURE_PATH) if issue.number == 5)
    links = extract_linked_references(issue, REPO)

    decision = evaluate_closure_policy(issue, links)

    assert decision.suitable_to_close is False
    assert decision.closure_reason == "not_suitable"
    assert decision.reason == "active_contribution_or_roadmap"
    assert decision.risk_level == "high"


def test_waiting_for_info_issue_can_be_suitable_to_close() -> None:
    issue = next(issue for issue in load_fixture_issues(FIXTURE_PATH) if issue.number == 6)
    links = extract_linked_references(issue, REPO)

    decision = evaluate_closure_policy(issue, links)

    assert decision.suitable_to_close is True
    assert decision.closure_reason == "stale_waiting_for_info"
    assert decision.evidence_refs
    assert decision.draft_comment is not None


def test_superseded_issue_uses_allowed_closure_reason() -> None:
    issue = IssueInput(
        number=7,
        title="Old tracker",
        body="This work migrated to owner/repo#456.",
        labels=["bug"],
        author="maintainer",
        url="https://github.com/owner/repo/issues/7",
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-02T00:00:00Z",
        comments=[
            IssueComment(
                author="maintainer",
                body="This is superseded by owner/repo#456.",
                created_at="2025-01-02T00:00:00Z",
            )
        ],
    )
    links = extract_linked_references(issue, "owner/repo")

    decision = evaluate_closure_policy(issue, links)

    assert decision.suitable_to_close is True
    assert decision.closure_reason == "superseded"
    assert decision.evidence_refs
