import json
from pathlib import Path

from typer.testing import CliRunner

from issue_agent.cli import app
from issue_agent.models import SummaryReport, WorkflowSummary
from issue_agent.state import write_summary_preview
from issue_agent.summary import build_summary_report


def test_summary_report_records_missing_workflows(tmp_path) -> None:
    report = build_summary_report(tmp_path)

    assert report.missing_workflows == ["classify", "answer", "close", "apply"]
    assert report.workflows["classify"].present is False
    assert report.github_mutation_applied is False


def test_summary_report_counts_fixture_generated_state(tmp_path) -> None:
    _write_fixture_preview_state(tmp_path)

    report = build_summary_report(tmp_path)

    assert report.missing_workflows == ["apply"]
    assert report.workflows["classify"].total_records == 6
    assert report.workflows["classify"].counts["policy_preview_ready"] >= 1
    assert report.workflows["answer"].counts["drafts_ready"] >= 1
    assert report.workflows["close"].counts["suitable_to_close"] >= 1
    assert report.workflows["close"].counts["high_risk"] >= 1


def test_write_summary_preview_creates_bounded_state(tmp_path) -> None:
    report = SummaryReport(
        workflows={
            "classify": WorkflowSummary(workflow="classify", present=True, total_records=1, counts={"policy_preview_ready": 1})
        },
        missing_workflows=["answer", "close", "apply"],
    )

    paths = write_summary_preview(tmp_path, report)

    assert paths["records"].exists()
    assert paths["latest_preview"].exists()
    data = json.loads(paths["records"].read_text(encoding="utf-8"))
    preview = paths["latest_preview"].read_text(encoding="utf-8")
    assert data["workflows"]["classify"]["total_records"] == 1
    assert "Mode: preview" in preview
    assert "no GitHub issues were changed" in preview


def test_reprocessing_summary_preview_replaces_report(tmp_path) -> None:
    first = SummaryReport(
        workflows={"classify": WorkflowSummary(workflow="classify", present=True, total_records=1)},
        missing_workflows=["answer", "close", "apply"],
    )
    second = SummaryReport(
        workflows={"classify": WorkflowSummary(workflow="classify", present=True, total_records=2)},
        missing_workflows=["answer", "close", "apply"],
    )

    write_summary_preview(tmp_path, first)
    write_summary_preview(tmp_path, second)

    data = json.loads((tmp_path / "summary" / "records.json").read_text(encoding="utf-8"))
    assert data["workflows"]["classify"]["total_records"] == 2


def test_summary_preview_cli_writes_local_artifacts(tmp_path) -> None:
    _write_fixture_preview_state(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "summary-preview",
            "--config",
            "examples/config.yaml",
            "--state-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "no GitHub issues were changed" in result.output
    assert (tmp_path / "summary" / "records.json").exists()
    assert (tmp_path / "summary" / "latest-preview.md").exists()


def test_summary_module_is_read_only_aggregation_boundary() -> None:
    source = Path("issue_agent/summary.py").read_text(encoding="utf-8")

    for forbidden in ["FixtureClassifierProvider", "evaluate_closure_policy", "GitHubMutationRunner", "run_codegraph"]:
        assert forbidden not in source


def _write_fixture_preview_state(state_root: Path) -> None:
    runner = CliRunner()
    commands = [
        [
            "preview",
            "--config",
            "examples/config.yaml",
            "--issues-file",
            "examples/issues.fixture.json",
            "--state-root",
            str(state_root),
        ],
        [
            "answer-preview",
            "--config",
            "examples/config.yaml",
            "--issues-file",
            "examples/issues.fixture.json",
            "--repo-root",
            "tests/fixtures/source_repo",
            "--state-root",
            str(state_root),
        ],
        [
            "close-preview",
            "--config",
            "examples/config.yaml",
            "--issues-file",
            "examples/issues.fixture.json",
            "--repo",
            "Kirrito-k423/issue-agent",
            "--state-root",
            str(state_root),
        ],
    ]
    for command in commands:
        result = runner.invoke(app, command)
        assert result.exit_code == 0, result.output
