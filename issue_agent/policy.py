from collections.abc import Sequence

from issue_agent.models import (
    AnswerPolicyDecision,
    ClassifierProposal,
    ClosureDecision,
    EvidenceRef,
    IssueInput,
    LabelRejection,
    LinkedReference,
    PolicyDecision,
)


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


def evaluate_closure_policy(
    issue: IssueInput,
    linked_references: Sequence[LinkedReference] | None = None,
) -> ClosureDecision:
    links = list(linked_references or [])
    text = f"{issue.title}\n{issue.body}\n" + "\n".join(comment.body for comment in issue.comments)
    normalized = text.lower()
    labels = {label.lower() for label in issue.labels}
    evidence_refs = [_evidence_from_link(ref) for ref in links]

    if _has_active_work_signal(issue, links):
        return ClosureDecision(
            issue_number=issue.number,
            suitable_to_close=False,
            closure_reason="not_suitable",
            risk_level="high",
            reason="active_contribution_or_roadmap",
            current_state="Issue carries roadmap/help-wanted or active contribution signals.",
            evidence_refs=evidence_refs,
            linked_references=links,
        )

    allowed_reason = _allowed_closure_reason(normalized, links)
    if allowed_reason is not None:
        draft_comment = (
            "Closing this issue based on the recorded evidence. "
            "If there is new information, please open a fresh issue with updated context."
        )
        return ClosureDecision(
            issue_number=issue.number,
            suitable_to_close=True,
            closure_reason=allowed_reason,
            risk_level="low" if allowed_reason in {"resolved", "duplicate", "superseded"} else "medium",
            reason=f"evidence_supports_{allowed_reason}",
            current_state=_current_state(issue, allowed_reason),
            evidence_refs=evidence_refs or [_issue_text_evidence(issue, allowed_reason)],
            linked_references=links,
            draft_comment=draft_comment,
        )

    return ClosureDecision(
        issue_number=issue.number,
        suitable_to_close=False,
        closure_reason="not_suitable",
        risk_level="high" if links else "medium",
        reason="insufficient_closure_evidence",
        current_state="No explicit closure reason evidence was found.",
        evidence_refs=evidence_refs,
        linked_references=links,
    )


def _has_active_work_signal(issue: IssueInput, links: Sequence[LinkedReference]) -> bool:
    labels = {label.lower() for label in issue.labels}
    title = issue.title.lower()
    protected_labels = {"help wanted", "good first issue", "roadmap"}
    if labels & protected_labels or "roadmap" in title or "call for contribution" in title:
        return True
    return any(ref.kind == "pull_request" and ref.status in {"open", "unknown"} for ref in links)


def _allowed_closure_reason(text: str, links: Sequence[LinkedReference]) -> str | None:
    relations = {ref.relation for ref in links}
    if "duplicate" in relations:
        return "duplicate"
    if "superseded_by" in relations:
        return "superseded"
    if "resolved_by" in relations:
        return "resolved"
    if "not supported" in text or "out of scope" in text or "unsupported" in text:
        return "unsupported"
    if "waiting_for_info" in relations or "please provide" in text or "need more information" in text:
        return "stale_waiting_for_info"
    return None


def _evidence_from_link(reference: LinkedReference) -> EvidenceRef:
    value = reference.url or f"{reference.repository}#{reference.number}"
    return EvidenceRef(kind="linked_reference", value=value, reason=reference.reason)


def _issue_text_evidence(issue: IssueInput, reason: str) -> EvidenceRef:
    return EvidenceRef(kind="issue", value=issue.url, reason=f"Issue text supports closure reason: {reason}.")


def _current_state(issue: IssueInput, closure_reason: str) -> str:
    return f"Issue #{issue.number} has explicit evidence for {closure_reason}; no public mutation has been applied."
