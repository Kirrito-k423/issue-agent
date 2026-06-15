from issue_agent.models import ClassifierProposal, LabelRejection, PolicyDecision


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
