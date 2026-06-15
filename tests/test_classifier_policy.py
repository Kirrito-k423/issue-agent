import pytest
from pydantic import ValidationError

from issue_agent.models import ClassifierProposal


def test_classifier_proposal_accepts_supported_category() -> None:
    proposal = ClassifierProposal(
        category="code_logic_question",
        confidence=0.82,
        proposed_action="preview_answer",
        evidence_needs=["source"],
        no_action_reason=None,
        labels_proposed=["question"],
        reason="The issue asks how repository code behaves.",
    )

    assert proposal.category == "code_logic_question"
    assert proposal.labels_proposed == ["question"]


def test_classifier_proposal_rejects_malformed_output() -> None:
    with pytest.raises(ValidationError):
        ClassifierProposal.model_validate(
            {
                "category": "unsupported",
                "confidence": 2.0,
                "proposed_action": "apply",
                "reason": "bad",
            }
        )


def test_all_required_categories_are_present_in_schema() -> None:
    schema = ClassifierProposal.model_json_schema()
    categories = set(schema["properties"]["category"]["enum"])

    assert {
        "experiment_reproduction",
        "code_logic_question",
        "usage_question",
        "stale_cleanup_candidate",
        "feature_enhancement",
        "bug_report",
        "unknown_unsafe",
    } <= categories
