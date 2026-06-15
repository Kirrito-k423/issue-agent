from issue_agent.models import ClassifierProposal, IssueInput
from issue_agent.policy import evaluate_answer_policy


def _issue() -> IssueInput:
    return IssueInput(
        number=10,
        title="Reproduction fails on NPU",
        body="Can you reproduce this environment issue?",
        labels=[],
        author="reporter",
        url="https://github.com/Kirrito-k423/issue-agent/issues/10",
        created_at="2026-06-10T00:00:00Z",
        updated_at="2026-06-10T00:00:00Z",
        comments=[],
    )


def _proposal(category: str) -> ClassifierProposal:
    return ClassifierProposal(
        category=category,
        confidence=0.8,
        proposed_action="preview_answer",
        evidence_needs=[],
        labels_proposed=["question"],
        reason="Fixture proposal.",
    )


def test_experiment_reproduction_without_run_evidence_is_not_reply_worthy() -> None:
    decision = evaluate_answer_policy(_issue(), _proposal("experiment_reproduction"), run_evidence=[])

    assert decision.reply_worthy is False
    assert decision.reason == "requires_unverified_reproduction"
    assert decision.status == "request_info"
