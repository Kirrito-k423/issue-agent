import json
from collections.abc import Sequence

from typer.testing import CliRunner

from issue_agent.apply import apply_close_actions
from issue_agent.cli import app
from issue_agent.github import GitHubCommandResult, GitHubMutationRunner
from issue_agent.models import ApplyAction
from issue_agent.state import write_apply_results


REPO = "Kirrito-k423/issue-agent"


def test_fixture_workflow_runs_preview_summary_and_fake_apply(tmp_path) -> None:
    runner = CliRunner()

    for command in [
        [
            "preview",
            "--config",
            "examples/config.yaml",
            "--issues-file",
            "examples/issues.fixture.json",
            "--state-root",
            str(tmp_path),
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
            str(tmp_path),
        ],
        [
            "close-preview",
            "--config",
            "examples/config.yaml",
            "--issues-file",
            "examples/issues.fixture.json",
            "--repo",
            REPO,
            "--state-root",
            str(tmp_path),
        ],
        [
            "summary-preview",
            "--config",
            "examples/config.yaml",
            "--state-root",
            str(tmp_path),
        ],
    ]:
        result = runner.invoke(app, command)
        assert result.exit_code == 0, result.output

    calls: list[list[str]] = []
    apply_results = apply_close_actions(
        tmp_path,
        REPO,
        [ApplyAction(issue_number=6, action_type="close")],
        mutation_runner=_fake_runner(calls),
    )
    write_apply_results(tmp_path, apply_results)

    result = runner.invoke(
        app,
        ["summary-preview", "--config", "examples/config.yaml", "--state-root", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    assert calls and calls[0][:3] == ["gh", "issue", "close"]
    for workflow in ["classify", "answer", "close", "apply", "summary"]:
        assert (tmp_path / workflow / "records.json").exists()

    for workflow in ["classify", "answer", "close"]:
        records = json.loads((tmp_path / workflow / "records.json").read_text(encoding="utf-8"))
        assert all(record["github_mutation_applied"] is False for record in records.values())

    summary = json.loads((tmp_path / "summary" / "records.json").read_text(encoding="utf-8"))
    assert summary["workflows"]["classify"]["total_records"] == 6
    assert summary["workflows"]["answer"]["counts"]["drafts_ready"] >= 1
    assert summary["workflows"]["close"]["counts"]["suitable_to_close"] >= 1
    assert summary["workflows"]["apply"]["counts"]["apply_applied"] == 1
    assert summary["workflows"]["apply"]["counts"]["mutations_applied"] == 1


def _fake_runner(calls: list[list[str]]) -> GitHubMutationRunner:
    def record_command(command: Sequence[str]) -> GitHubCommandResult:
        calls.append(list(command))
        return GitHubCommandResult(command=list(command), returncode=0)

    return GitHubMutationRunner(REPO, executor=record_command)
