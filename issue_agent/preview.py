from collections.abc import Iterable

from issue_agent.models import PreviewRecord


def render_classification_preview(records: Iterable[PreviewRecord]) -> str:
    lines = [
        "# Issue Agent Classification Preview",
        "",
        "Mode: preview",
        "Safety: no GitHub issues were changed.",
        "",
        "| Issue | Title | Category | Proposed | Applyable | Rejected | Status | Reason |",
        "|-------|-------|----------|----------|-----------|----------|--------|--------|",
    ]
    for record in records:
        proposal = record.model_proposal
        policy = record.policy_decision
        title = record.title.replace("|", "\\|")
        proposed = ", ".join(proposal.labels_proposed) or "-"
        applyable = ", ".join(policy.labels_applyable) or "-"
        rejected = ", ".join(f"{item.name}:{item.reason}" for item in policy.labels_rejected) or "-"
        reason = policy.reason.replace("|", "\\|")
        lines.append(
            f"| #{record.issue_number} | {title} | {proposal.category} | {proposed} | "
            f"{applyable} | {rejected} | {policy.status} | {reason} |"
        )
    lines.append("")
    return "\n".join(lines)
