from collections.abc import Sequence

from issue_agent.models import AnswerPolicyDecision, ClassifierProposal, EvidenceRef, IssueInput, LabelRejection, PolicyDecision


def apply_policy(proposal: ClassifierProposal, available_labels: set[str]) -> PolicyDecision:
    labels_applyable = [label for label in proposal.labels_proposed if label in available_labels]
    labels_rejected = [
        LabelRejection(name=label, reason="label_not_in_repository")
        for label in proposal.labels_proposed
        if label not in available_labels
    ]

    if proposal.category == "unknown_unsafe":
        return PolicyDecision(
            labels_applyable=[],
            labels_rejected=labels_rejected,
            status="human_review",
            reason=proposal.no_action_reason or "unknown_unsafe",
        )

    return PolicyDecision(
        labels_applyable=labels_applyable,
        labels_rejected=labels_rejected,
        status="preview_ready",
        reason="preview_only_policy_passed",
    )


def evaluate_answer_policy(
    issue: IssueInput,
    proposal: ClassifierProposal,
    source_evidence: Sequence[EvidenceRef] | None = None,
    run_evidence: Sequence[EvidenceRef] | None = None,
) -> AnswerPolicyDecision:
    del issue
    source_refs = list(source_evidence or [])
    run_refs = list(run_evidence or [])

    if proposal.category == "experiment_reproduction" and not run_refs:
        return AnswerPolicyDecision(
            reply_worthy=False,
            status="request_info",
            reason="requires_unverified_reproduction",
            required_evidence=["run_evidence"],
        )

    if proposal.category == "unknown_unsafe" or proposal.confidence < 0.5:
        return AnswerPolicyDecision(
            reply_worthy=False,
            status="human_review",
            reason=proposal.no_action_reason or "unknown_unsafe",
            required_evidence=proposal.evidence_needs or ["human_review"],
        )

    if proposal.category not in {"code_logic_question", "usage_question", "experiment_reproduction"}:
        return AnswerPolicyDecision(
            reply_worthy=False,
            status="skipped",
            reason="unsupported_answer_category",
            required_evidence=[],
        )

    if proposal.category == "code_logic_question" and not _has_source_evidence(source_refs):
        return AnswerPolicyDecision(
            reply_worthy=False,
            status="human_review",
            reason="missing_source_evidence",
            required_evidence=["source_evidence"],
        )

    return AnswerPolicyDecision(
        reply_worthy=True,
        status="draft_ready",
        reason="evidence_policy_passed",
        required_evidence=[] if source_refs or run_refs else [],
    )


def _has_source_evidence(evidence_refs: Sequence[EvidenceRef]) -> bool:
    return any(ref.kind == "source" and bool(ref.path) for ref in evidence_refs)
