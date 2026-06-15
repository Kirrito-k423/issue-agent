from issue_agent.models import EvidenceRef


def test_source_evidence_ref_serializes_lookup_fields() -> None:
    evidence = EvidenceRef(
        kind="source",
        value="example_module.py",
        reason="Shows the preview safety check.",
        lookup_mode="codegraph",
        path="example_module.py",
        symbol="preview_safety",
        snippet="def preview_safety() -> str:",
        line_start=1,
        line_end=3,
        codegraph_available=True,
    )

    serialized = evidence.model_dump(mode="json")

    assert serialized["lookup_mode"] == "codegraph"
    assert serialized["path"] == "example_module.py"
    assert serialized["snippet"]


def test_minimal_evidence_ref_remains_supported() -> None:
    evidence = EvidenceRef(kind="issue", value="#1", reason="Issue body asks a question.")

    assert evidence.kind == "issue"
    assert evidence.lookup_mode is None
