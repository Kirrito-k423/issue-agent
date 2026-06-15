import json
from pathlib import Path
from typing import Any

from issue_agent.preview import render_classification_preview


def _read_records(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("records.json must be a JSON object")
    return raw


def write_batch_preview(state_root: Path, workflow: str, records: list[dict]) -> dict[str, Path]:
    workflow_root = state_root / workflow
    workflow_root.mkdir(parents=True, exist_ok=True)

    records_path = workflow_root / "records.json"
    pending_path = workflow_root / "pending-batch.json"
    preview_path = workflow_root / "latest-preview.md"

    current = _read_records(records_path)
    for record in records:
        number = record.get("issue_number", record.get("number"))
        if number is None:
            raise ValueError("preview record is missing issue_number")
        current[str(number)] = record

    records_path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pending_path.write_text(
        json.dumps({"mode": "preview", "workflow": workflow, "records": records}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    preview_path.write_text(render_classification_preview(records), encoding="utf-8")

    return {
        "records": records_path,
        "pending_batch": pending_path,
        "latest_preview": preview_path,
    }
