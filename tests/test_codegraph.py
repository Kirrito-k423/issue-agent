from pathlib import Path
from types import SimpleNamespace

from issue_agent.codegraph import has_codegraph_index, lookup_source_evidence
from issue_agent.models import EvidenceRef


FIXTURE_REPO = Path("tests/fixtures/source_repo")


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


def test_has_codegraph_index_detects_fixture_repo() -> None:
    assert has_codegraph_index(FIXTURE_REPO)


def test_lookup_uses_codegraph_before_fallback_when_index_exists() -> None:
    calls: list[list[str]] = []

    def runner(argv: list[str]) -> SimpleNamespace:
        calls.append(argv)
        return SimpleNamespace(
            returncode=0,
            stdout="example_module.py:1:def preview_safety() -> str:",
            stderr="",
        )

    evidence = lookup_source_evidence(FIXTURE_REPO, "preview safety", runner=runner)

    assert calls[0][:2] == ["codegraph", "explore"]
    assert calls[0][2] == "preview safety"
    assert evidence[0].lookup_mode == "codegraph"
    assert evidence[0].codegraph_available is True
    assert evidence[0].path == "example_module.py"
