import json
from collections.abc import Iterable
from pathlib import Path

from issue_agent.github import GitHubMutationRunner
from issue_agent.models import ApplyAction, ApplyResult, ClosureDecision


class ApplyValidationError(ValueError):
    """Raised when an apply request is not backed by a reviewed preview."""


_ACTION_ORDER = {
    "add_label": 10,
    "remove_label": 20,
    "comment": 30,
    "close": 40,
}


def load_close_preview_records(state_root: Path) -> dict[int, ClosureDecision]:
    records_path = state_root / "close" / "records.json"
    if not records_path.exists():
        raise ApplyValidationError(f"missing close preview records: {records_path}")

    raw = json.loads(records_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ApplyValidationError("close preview records must be a JSON object")

    records: dict[int, ClosureDecision] = {}
    for issue_number, payload in raw.items():
        record = ClosureDecision.model_validate(payload)
        records[int(issue_number)] = record
    return records


def validate_apply_action(preview_records: dict[int, ClosureDecision], action: ApplyAction) -> ClosureDecision:
    preview_record = preview_records.get(action.issue_number)
    if preview_record is None:
        raise ApplyValidationError(f"missing close preview record for issue #{action.issue_number}")

    if action.action_type in {"add_label", "remove_label"}:
        if not action.value:
            raise ApplyValidationError(f"{action.action_type} requires a label value")
        return preview_record

    if action.action_type == "comment":
        _validate_suitable_closure_preview(preview_record, action)
        return preview_record

    if action.action_type == "close":
        _validate_suitable_closure_preview(preview_record, action)
        return preview_record

    raise ApplyValidationError(f"unsupported apply action: {action.action_type}")


def apply_close_actions(
    state_root: Path,
    repo: str,
    actions: Iterable[ApplyAction],
    mutation_runner: GitHubMutationRunner | None = None,
) -> list[ApplyResult]:
    preview_records = load_close_preview_records(state_root)
    action_list = sorted(
        list(actions),
        key=lambda action: (
            action.issue_number,
            _ACTION_ORDER[action.action_type],
            action.value or "",
            action.body or "",
        ),
    )

    for action in action_list:
        validate_apply_action(preview_records, action)

    runner = mutation_runner or GitHubMutationRunner(repo)
    results: list[ApplyResult] = []
    failed_comments: set[int] = set()

    for action in action_list:
        preview_record = preview_records[action.issue_number]
        if action.action_type == "close" and action.requires_comment and action.issue_number in failed_comments:
            results.append(_skipped_result(action, "required comment action failed"))
            continue

        result = _execute_action(runner, preview_record, action)
        if action.action_type == "comment" and result.status == "failed":
            failed_comments.add(action.issue_number)
        results.append(result)

    return results


def _validate_suitable_closure_preview(preview_record: ClosureDecision, action: ApplyAction) -> None:
    if not preview_record.suitable_to_close:
        raise ApplyValidationError(f"issue #{action.issue_number} preview is not suitable to close")
    if not preview_record.draft_comment:
        raise ApplyValidationError(f"issue #{action.issue_number} preview has no draft close comment")
    if action.body is not None and action.body != preview_record.draft_comment:
        raise ApplyValidationError(f"issue #{action.issue_number} action body does not match preview draft")


def _execute_action(
    runner: GitHubMutationRunner,
    preview_record: ClosureDecision,
    action: ApplyAction,
) -> ApplyResult:
    if action.action_type == "add_label":
        command_result = runner.add_label(action.issue_number, action.value or "")
    elif action.action_type == "remove_label":
        command_result = runner.remove_label(action.issue_number, action.value or "")
    elif action.action_type == "comment":
        command_result = runner.post_comment(action.issue_number, action.body or preview_record.draft_comment or "")
    else:
        close_comment = None if action.requires_comment else action.body or preview_record.draft_comment
        command_result = runner.close_issue(
            action.issue_number,
            comment=close_comment,
            reason=action.value or _default_close_reason(preview_record),
        )

    if command_result.returncode == 0:
        return ApplyResult(
            action_id=_action_id(action),
            issue_number=action.issue_number,
            action_type=action.action_type,
            status="applied",
            command=command_result.command,
            github_mutation_applied=True,
        )

    return ApplyResult(
        action_id=_action_id(action),
        issue_number=action.issue_number,
        action_type=action.action_type,
        status="failed",
        command=command_result.command,
        error=command_result.stderr or f"gh exited with code {command_result.returncode}",
        github_mutation_applied=False,
    )


def _skipped_result(action: ApplyAction, reason: str) -> ApplyResult:
    return ApplyResult(
        action_id=_action_id(action),
        issue_number=action.issue_number,
        action_type=action.action_type,
        status="skipped",
        error=reason,
        github_mutation_applied=False,
    )


def _default_close_reason(preview_record: ClosureDecision) -> str:
    return "completed" if preview_record.closure_reason == "resolved" else "not planned"


def _action_id(action: ApplyAction) -> str:
    suffix = action.value or ("with-comment" if action.body else "default")
    safe_suffix = suffix.replace(" ", "-").replace("/", "-")
    return f"{action.issue_number}:{action.action_type}:{safe_suffix}"
