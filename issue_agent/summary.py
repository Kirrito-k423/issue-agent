import json
from pathlib import Path
from typing import Any

from issue_agent.models import SummaryReport, WorkflowSummary


SUMMARY_WORKFLOWS = ("classify", "answer", "close", "apply")


def build_summary_report(state_root: Path) -> SummaryReport:
    workflows: dict[str, WorkflowSummary] = {}
    missing_workflows: list[str] = []

    for workflow in SUMMARY_WORKFLOWS:
        records_path = state_root / workflow / "records.json"
        records = _read_workflow_records(records_path)
        if records is None:
            missing_workflows.append(workflow)
            workflows[workflow] = WorkflowSummary(workflow=workflow, present=False)
            continue
        workflows[workflow] = WorkflowSummary(
            workflow=workflow,
            present=True,
            total_records=len(records),
            counts=_workflow_counts(workflow, records),
        )

    return SummaryReport(workflows=workflows, missing_workflows=missing_workflows)


def _read_workflow_records(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return raw


def _workflow_counts(workflow: str, records: dict[str, Any]) -> dict[str, int]:
    if workflow == "classify":
        return _classification_counts(records)
    if workflow == "answer":
        return _answer_counts(records)
    if workflow == "close":
        return _close_counts(records)
    if workflow == "apply":
        return _apply_counts(records)
    return {}


def _classification_counts(records: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {"mutations_applied": 0}
    for record in records.values():
        if not isinstance(record, dict):
            continue
        proposal = record.get("model_proposal") if isinstance(record.get("model_proposal"), dict) else {}
        policy = record.get("policy_decision") if isinstance(record.get("policy_decision"), dict) else {}
        _increment(counts, f"category_{proposal.get('category', 'unknown')}")
        _increment(counts, f"policy_{policy.get('status', 'unknown')}")
        if record.get("github_mutation_applied") is True:
            counts["mutations_applied"] += 1
    return counts


def _answer_counts(records: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {"drafts_ready": 0, "mutations_applied": 0}
    for record in records.values():
        if not isinstance(record, dict):
            continue
        answer_policy = record.get("answer_policy") if isinstance(record.get("answer_policy"), dict) else {}
        _increment(counts, f"answer_{answer_policy.get('status', 'unknown')}")
        if answer_policy.get("reply_worthy") is True or record.get("draft_path"):
            counts["drafts_ready"] += 1
        if record.get("github_mutation_applied") is True:
            counts["mutations_applied"] += 1
    return counts


def _close_counts(records: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {
        "suitable_to_close": 0,
        "high_risk": 0,
        "mutations_applied": 0,
    }
    for record in records.values():
        if not isinstance(record, dict):
            continue
        _increment(counts, f"closure_{record.get('closure_reason', 'unknown')}")
        _increment(counts, f"risk_{record.get('risk_level', 'unknown')}")
        if record.get("suitable_to_close") is True:
            counts["suitable_to_close"] += 1
        if record.get("risk_level") == "high":
            counts["high_risk"] += 1
        if record.get("github_mutation_applied") is True:
            counts["mutations_applied"] += 1
    return counts


def _apply_counts(records: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {"mutations_applied": 0}
    for record in records.values():
        if not isinstance(record, dict):
            continue
        _increment(counts, f"apply_{record.get('status', 'unknown')}")
        _increment(counts, f"action_{record.get('action_type', 'unknown')}")
        if record.get("github_mutation_applied") is True:
            counts["mutations_applied"] += 1
    return counts


def _increment(counts: dict[str, int], key: str) -> None:
    counts[key] = counts.get(key, 0) + 1
