from pathlib import Path

from issue_agent.answer import build_answer_preview_records
from issue_agent.classifier import FixtureClassifierProvider
from issue_agent.github import load_fixture_issues
from issue_agent.models import EvidenceRef


FIXTURE_ISSUES = Path("examples/issues.fixture.json")


def _source_lookup(_: Path, __: str) -> list[EvidenceRef]:
    return [
        EvidenceRef(
            kind="source",
            value="example_module.py",
            reason="Shows preview safety.",
            lookup_mode="fallback_search",
            path="example_module.py",
            snippet="def preview_safety() -> str:",
        )
    ]


def test_answer_preview_records_include_source_evidence_for_code_questions() -> None:
    issues = load_fixture_issues(FIXTURE_ISSUES)

    records = build_answer_preview_records(issues, Path("tests/fixtures/source_repo"), FixtureClassifierProvider(), _source_lookup)
    code_record = next(record for record in records if record.issue_number == 3)

    assert any(ref.kind == "source" for ref in code_record.evidence_refs)
    assert code_record.answer_policy is not None
    assert code_record.answer_policy.reply_worthy is True
    assert code_record.github_mutation_applied is False


def test_reproduction_issues_do_not_get_draft_paths_without_run_evidence() -> None:
    issues = load_fixture_issues(FIXTURE_ISSUES)

    records = build_answer_preview_records(issues, Path("tests/fixtures/source_repo"), FixtureClassifierProvider(), _source_lookup)
    reproduction_record = next(record for record in records if record.issue_number == 4)

    assert reproduction_record.answer_policy is not None
    assert reproduction_record.answer_policy.reply_worthy is False
    assert reproduction_record.answer_policy.reason == "requires_unverified_reproduction"
    assert reproduction_record.draft_path is None
    assert reproduction_record.github_mutation_applied is False
