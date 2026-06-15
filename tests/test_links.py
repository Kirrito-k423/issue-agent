from issue_agent.models import LinkedReference
from issue_agent.links import extract_linked_references
from issue_agent.models import IssueInput, IssueComment


def test_linked_reference_serializes_structured_fields() -> None:
    reference = LinkedReference(
        repository="owner/repo",
        number=123,
        kind="issue",
        relation="duplicate",
        source="body",
        reason="Issue body links to the canonical tracker.",
        status="open",
        url="https://github.com/owner/repo/issues/123",
    )

    serialized = reference.model_dump(mode="json")

    assert serialized["repository"] == "owner/repo"
    assert serialized["number"] == 123
    assert serialized["relation"] == "duplicate"


def test_unknown_link_status_is_not_a_closure_reason() -> None:
    reference = LinkedReference(
        repository="owner/repo",
        number=456,
        kind="unknown",
        relation="mentions",
        source="comment:0",
        reason="Comment mentions a related thread.",
    )

    assert reference.status == "unknown"
    assert reference.relation == "mentions"


def test_extracts_short_reference_from_body_with_default_repo() -> None:
    issue = _issue(body="Duplicate of #123, please use that canonical tracker.")

    references = extract_linked_references(issue, "owner/repo")

    assert references[0].repository == "owner/repo"
    assert references[0].number == 123
    assert references[0].kind == "unknown"
    assert references[0].relation == "duplicate"


def test_extracts_cross_repo_reference_from_comment() -> None:
    issue = _issue(
        comments=[
            IssueComment(
                author="maintainer",
                body="This is superseded by owner/repo#456.",
                created_at="2026-06-01T00:00:00Z",
            )
        ]
    )

    references = extract_linked_references(issue, "owner/repo")

    assert references[0].repository == "owner/repo"
    assert references[0].number == 456
    assert references[0].source == "comment:0"
    assert references[0].relation == "superseded_by"


def test_extracts_pull_request_url_kind() -> None:
    issue = _issue(body="Fixed by https://github.com/owner/repo/pull/789.")

    references = extract_linked_references(issue, "owner/repo")

    assert references[0].kind == "pull_request"
    assert references[0].number == 789
    assert references[0].relation == "resolved_by"


def _issue(body: str = "", comments: list[IssueComment] | None = None) -> IssueInput:
    return IssueInput(
        number=99,
        title="Linked reference fixture",
        body=body,
        labels=[],
        author="maintainer",
        url="https://github.com/owner/repo/issues/99",
        created_at="2026-06-01T00:00:00Z",
        updated_at="2026-06-01T00:00:00Z",
        comments=comments or [],
    )
