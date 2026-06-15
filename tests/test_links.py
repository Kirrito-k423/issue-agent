from issue_agent.models import LinkedReference


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
