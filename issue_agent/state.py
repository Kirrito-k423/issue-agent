import json
from pathlib import Path
from typing import Any

from issue_agent.answer import render_answer_draft
from issue_agent.models import ApplyResult, BatchPreview, ClosureDecision, PreviewRecord, SummaryReport
from issue_agent.preview import (
    render_answer_preview,
    render_apply_results,
    render_classification_preview,
    render_close_preview,
    render_summary_preview,
)


def _read_records(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("records.json must be a JSON object")
    return raw


def write_batch_preview(state_root: Path, workflow: str, records: list[PreviewRecord]) -> dict[str, Path]:
    workflow_root = state_root / workflow
    workflow_root.mkdir(parents=True, exist_ok=True)

    records_path = workflow_root / "records.json"
    pending_path = workflow_root / "pending-batch.json"
    preview_path = workflow_root / "latest-preview.md"

    batch = BatchPreview(workflow=workflow, records=records)

    current = _read_records(records_path)
    for record in batch.records:
        current[str(record.issue_number)] = record.model_dump(mode="json")
    records_path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pending_path.write_text(
        json.dumps(batch.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    preview_path.write_text(render_classification_preview(batch.records), encoding="utf-8")

    return {
        "records": records_path,
        "pending_batch": pending_path,
        "latest_preview": preview_path,
    }


def write_answer_preview(state_root: Path, records: list[PreviewRecord]) -> dict[str, Path]:
    workflow_root = state_root / "answer"
    drafts_root = workflow_root / "drafts"
    workflow_root.mkdir(parents=True, exist_ok=True)
    drafts_root.mkdir(parents=True, exist_ok=True)

    for record in records:
        draft_path = drafts_root / f"issue-{record.issue_number}.md"
        if record.answer_policy is not None and record.answer_policy.reply_worthy:
            relative_draft_path = Path("answer") / "drafts" / draft_path.name
            record.draft_path = relative_draft_path.as_posix()
            record.answer_policy.draft_path = record.draft_path
            draft_path.write_text(render_answer_draft(record), encoding="utf-8")
        else:
            record.draft_path = None
            if record.answer_policy is not None:
                record.answer_policy.draft_path = None
            draft_path.unlink(missing_ok=True)

    records_path = workflow_root / "records.json"
    pending_path = workflow_root / "pending-batch.json"
    preview_path = workflow_root / "latest-preview.md"

    batch = BatchPreview(workflow="answer", records=records)
    current = _read_records(records_path)
    for record in batch.records:
        current[str(record.issue_number)] = record.model_dump(mode="json")
    records_path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pending_path.write_text(
        json.dumps(batch.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    preview_path.write_text(render_answer_preview(batch.records), encoding="utf-8")

    return {
        "records": records_path,
        "pending_batch": pending_path,
        "latest_preview": preview_path,
        "drafts": drafts_root,
    }


def write_close_preview(state_root: Path, records: list[ClosureDecision]) -> dict[str, Path]:
    workflow_root = state_root / "close"
    workflow_root.mkdir(parents=True, exist_ok=True)

    records_path = workflow_root / "records.json"
    pending_path = workflow_root / "pending-batch.json"
    preview_path = workflow_root / "latest-preview.md"

    current = _read_records(records_path)
    serialized_records = [record.model_dump(mode="json") for record in records]
    for record in serialized_records:
        current[str(record["issue_number"])] = record

    batch = {
        "mode": "preview",
        "workflow": "close",
        "records": serialized_records,
    }
    records_path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pending_path.write_text(json.dumps(batch, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    preview_path.write_text(render_close_preview(records), encoding="utf-8")

    return {
        "records": records_path,
        "pending_batch": pending_path,
        "latest_preview": preview_path,
    }


def write_apply_results(state_root: Path, records: list[ApplyResult]) -> dict[str, Path]:
    workflow_root = state_root / "apply"
    workflow_root.mkdir(parents=True, exist_ok=True)

    records_path = workflow_root / "records.json"
    preview_path = workflow_root / "latest-preview.md"

    current = _read_records(records_path)
    for record in records:
        current[record.action_id] = record.model_dump(mode="json")

    records_path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    preview_path.write_text(render_apply_results(records), encoding="utf-8")

    return {
        "records": records_path,
        "latest_preview": preview_path,
    }


def write_summary_preview(state_root: Path, report: SummaryReport) -> dict[str, Path]:
    workflow_root = state_root / "summary"
    workflow_root.mkdir(parents=True, exist_ok=True)

    records_path = workflow_root / "records.json"
    preview_path = workflow_root / "latest-preview.md"

    records_path.write_text(json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    preview_path.write_text(render_summary_preview(report), encoding="utf-8")

    return {
        "records": records_path,
        "latest_preview": preview_path,
    }
