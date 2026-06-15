import json

from issue_agent.models import ClassifierProposal, PolicyDecision, PreviewRecord
from issue_agent.state import write_batch_preview


def _record(issue_number: int, title: str) -> PreviewRecord:
    proposal = ClassifierProposal(
        category="usage_question",
        confidence=0.8,
        proposed_action="preview_classification",
        evidence_needs=[],
        labels_proposed=["question"],
        reason="Fixture question.",
    )
    decision = PolicyDecision(
        labels_applyable=["question"],
        labels_rejected=[],
        status="preview_ready",
        reason="preview_only_policy_passed",
    )
    return PreviewRecord(
        issue_number=issue_number,
        title=title,
        model_proposal=proposal,
        policy_decision=decision,
    )


def test_reprocessing_issue_replaces_records_entry(tmp_path) -> None:
    write_batch_preview(tmp_path, "classify", [_record(1, "First title")])
    write_batch_preview(tmp_path, "classify", [_record(1, "Replacement title")])

    records = json.loads((tmp_path / "classify" / "records.json").read_text(encoding="utf-8"))

    assert list(records) == ["1"]
    assert records["1"]["title"] == "Replacement title"


def test_pending_batch_contains_model_and_policy_fields(tmp_path) -> None:
    write_batch_preview(tmp_path, "classify", [_record(1, "Question title")])

    pending = json.loads((tmp_path / "classify" / "pending-batch.json").read_text(encoding="utf-8"))
    preview = (tmp_path / "classify" / "latest-preview.md").read_text(encoding="utf-8")

    assert "model_proposal" in pending["records"][0]
    assert "policy_decision" in pending["records"][0]
    assert "Category" in preview
    assert "Applyable" in preview
    assert "Rejected" in preview
    assert "Status" in preview
