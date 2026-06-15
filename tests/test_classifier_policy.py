from pathlib import Path

import pytest
from pydantic import ValidationError

from issue_agent.classifier import FixtureClassifierProvider, parse_or_human_review
from issue_agent.github import load_fixture_issues
from issue_agent.models import ClassifierProposal
from issue_agent.policy import apply_policy


FIXTURE_PATH = Path("examples/issues.fixture.json")


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


def test_fixture_provider_classifies_fixture_issues() -> None:
    issues = load_fixture_issues(FIXTURE_PATH)
    provider = FixtureClassifierProvider()

    proposals = [provider.classify(issue) for issue in issues]

    assert proposals[0].category == "usage_question"
    assert proposals[0].labels_proposed == ["question"]
    assert proposals[1].category == "bug_report"
    assert proposals[1].labels_proposed == ["bug"]


def test_policy_rejects_labels_missing_from_repository() -> None:
    proposal = ClassifierProposal(
        category="bug_report",
        confidence=0.8,
        proposed_action="preview_classification",
        evidence_needs=[],
        labels_proposed=["bug", "missing-label"],
        reason="Bug signal found.",
    )

    decision = apply_policy(proposal, {"bug"})

    assert decision.labels_applyable == ["bug"]
    assert decision.labels_rejected[0].name == "missing-label"
    assert decision.labels_rejected[0].reason == "label_not_in_repository"


def test_invalid_model_json_is_repaired_at_most_once() -> None:
    calls = 0
    repaired = ClassifierProposal(
        category="usage_question",
        confidence=0.7,
        proposed_action="preview_classification",
        evidence_needs=[],
        labels_proposed=["question"],
        reason="Repaired.",
    ).model_dump_json()

    def repair(_: str) -> str:
        nonlocal calls
        calls += 1
        return repaired

    parsed = parse_or_human_review("{not-json", repair=repair)

    assert calls == 1
    assert isinstance(parsed, ClassifierProposal)
    assert parsed.category == "usage_question"


def test_unresolved_invalid_output_becomes_human_review() -> None:
    calls = 0

    def repair(_: str) -> str:
        nonlocal calls
        calls += 1
        return '{"category": "bad"}'

    parsed = parse_or_human_review("{not-json", repair=repair)

    assert calls == 1
    assert parsed.status == "human_review"
    assert parsed.reason == "invalid_classifier_output"


def test_repair_exception_becomes_human_review() -> None:
    def repair(_: str) -> str:
        raise RuntimeError("repair provider failed")

    parsed = parse_or_human_review("{not-json", repair=repair)

    assert parsed.status == "human_review"
    assert parsed.reason == "invalid_classifier_output"
