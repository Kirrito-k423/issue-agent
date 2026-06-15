import json
from collections.abc import Sequence
from pathlib import Path

import pytest

from issue_agent.apply import ApplyValidationError, apply_close_actions, load_close_preview_records, validate_apply_action
from issue_agent.closure import build_close_preview_records
from issue_agent.github import GitHubCommandResult, GitHubMutationRunner, load_fixture_issues
from issue_agent.models import ApplyAction
from issue_agent.state import write_apply_results, write_close_preview


FIXTURE_PATH = Path("examples/issues.fixture.json")
REPO = "Kirrito-k423/issue-agent"


def test_missing_preview_state_is_rejected(tmp_path) -> None:
    action = ApplyAction(issue_number=6, action_type="close")

    with pytest.raises(ApplyValidationError, match="missing close preview records"):
        apply_close_actions(tmp_path, REPO, [action], mutation_runner=_fake_runner([]))


def test_mismatched_close_action_is_rejected(tmp_path) -> None:
    _write_close_preview(tmp_path)
    action = ApplyAction(issue_number=5, action_type="close")

    with pytest.raises(ApplyValidationError, match="not suitable to close"):
        apply_close_actions(tmp_path, REPO, [action], mutation_runner=_fake_runner([]))


def test_apply_validation_does_not_call_closure_policy(tmp_path, monkeypatch) -> None:
    _write_close_preview(tmp_path)

    def fail_policy_call(*_args, **_kwargs):  # pragma: no cover - only runs if apply crosses the boundary
        raise AssertionError("apply validation must not call closure policy")

    import issue_agent.policy

    monkeypatch.setattr(issue_agent.policy, "evaluate_closure_policy", fail_policy_call)
    records = load_close_preview_records(tmp_path)
    validate_apply_action(records, ApplyAction(issue_number=6, action_type="comment"))


def test_fake_runner_records_label_comment_and_close_commands(tmp_path) -> None:
    records = _write_close_preview(tmp_path)
    draft = records[6].draft_comment
    calls: list[list[str]] = []
    runner = _fake_runner(calls)

    results = apply_close_actions(
        tmp_path,
        REPO,
        [
            ApplyAction(issue_number=6, action_type="close"),
            ApplyAction(issue_number=6, action_type="comment"),
            ApplyAction(issue_number=6, action_type="add_label", value="stale-cleanup"),
        ],
        mutation_runner=runner,
    )

    assert [result.status for result in results] == ["applied", "applied", "applied"]
    assert calls == [
        ["gh", "issue", "edit", "6", "--add-label", "stale-cleanup", "--repo", REPO],
        ["gh", "issue", "comment", "6", "--body", draft, "--repo", REPO],
        ["gh", "issue", "close", "6", "--comment", draft, "--reason", "not planned", "--repo", REPO],
    ]


def test_comment_failure_skips_dependent_close_without_retry(tmp_path) -> None:
    _write_close_preview(tmp_path)
    calls: list[list[str]] = []

    def fail_comment(command: Sequence[str]) -> GitHubCommandResult:
        calls.append(list(command))
        return GitHubCommandResult(command=list(command), returncode=1, stderr="comment failed")

    runner = GitHubMutationRunner(REPO, executor=fail_comment)
    results = apply_close_actions(
        tmp_path,
        REPO,
        [
            ApplyAction(issue_number=6, action_type="comment"),
            ApplyAction(issue_number=6, action_type="close", requires_comment=True),
        ],
        mutation_runner=runner,
    )

    assert [result.status for result in results] == ["failed", "skipped"]
    assert results[0].error == "comment failed"
    assert results[1].error == "required comment action failed"
    assert len(calls) == 1
    assert calls[0][:3] == ["gh", "issue", "comment"]


def test_apply_results_preserve_close_preview_state(tmp_path) -> None:
    _write_close_preview(tmp_path)
    runner = _fake_runner([])
    results = apply_close_actions(
        tmp_path,
        REPO,
        [ApplyAction(issue_number=6, action_type="close")],
        mutation_runner=runner,
    )

    paths = write_apply_results(tmp_path, results)

    assert paths["records"].exists()
    assert paths["latest_preview"].exists()
    assert (tmp_path / "close" / "records.json").exists()
    close_records = json.loads((tmp_path / "close" / "records.json").read_text(encoding="utf-8"))
    apply_records = json.loads(paths["records"].read_text(encoding="utf-8"))
    assert close_records["6"]["github_mutation_applied"] is False
    assert next(iter(apply_records.values()))["github_mutation_applied"] is True


def _write_close_preview(state_root: Path):
    issues = load_fixture_issues(FIXTURE_PATH)
    records = build_close_preview_records(issues, REPO)
    write_close_preview(state_root, records)
    return {record.issue_number: record for record in records}


def _fake_runner(calls: list[list[str]]) -> GitHubMutationRunner:
    def record_command(command: Sequence[str]) -> GitHubCommandResult:
        calls.append(list(command))
        return GitHubCommandResult(command=list(command), returncode=0)

    return GitHubMutationRunner(REPO, executor=record_command)
