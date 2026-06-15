from pathlib import Path

from typer.testing import CliRunner

from issue_agent.answer import build_answer_preview_records
from issue_agent.classifier import FixtureClassifierProvider
from issue_agent.cli import app
from issue_agent.github import load_fixture_issues
from issue_agent.models import EvidenceRef
from issue_agent.state import write_answer_preview


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


def test_write_answer_preview_creates_bounded_state_and_drafts(tmp_path) -> None:
    issues = load_fixture_issues(FIXTURE_ISSUES)
    records = build_answer_preview_records(issues, Path("tests/fixtures/source_repo"), FixtureClassifierProvider(), _source_lookup)

    paths = write_answer_preview(tmp_path, records)

    assert paths["records"].exists()
    assert paths["pending_batch"].exists()
    assert paths["latest_preview"].exists()
    assert (tmp_path / "answer" / "drafts" / "issue-3.md").exists()
    assert not (tmp_path / "answer" / "drafts" / "issue-4.md").exists()


def test_reprocessing_answer_preview_replaces_records_entry(tmp_path) -> None:
    issues = load_fixture_issues(FIXTURE_ISSUES)
    records = build_answer_preview_records(issues, Path("tests/fixtures/source_repo"), FixtureClassifierProvider(), _source_lookup)
    code_record = [record for record in records if record.issue_number == 3]

    write_answer_preview(tmp_path, code_record)
    code_record[0].title = "Replacement title"
    write_answer_preview(tmp_path, code_record)

    import json

    data = json.loads((tmp_path / "answer" / "records.json").read_text(encoding="utf-8"))
    assert list(data) == ["3"]
    assert data["3"]["title"] == "Replacement title"
    assert data["3"]["draft_path"] == "answer/drafts/issue-3.md"


def test_answer_preview_cli_writes_local_artifacts(tmp_path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "answer-preview",
            "--config",
            "examples/config.yaml",
            "--issues-file",
            "examples/issues.fixture.json",
            "--repo-root",
            "tests/fixtures/source_repo",
            "--state-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "no GitHub comments were posted" in result.output
    assert (tmp_path / "answer" / "records.json").exists()
    assert (tmp_path / "answer" / "pending-batch.json").exists()
    assert (tmp_path / "answer" / "latest-preview.md").exists()
    assert (tmp_path / "answer" / "drafts" / "issue-3.md").exists()
