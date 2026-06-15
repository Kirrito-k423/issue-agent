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


def render_answer_preview(records: Iterable[PreviewRecord]) -> str:
    lines = [
        "# Issue Agent Answer Preview",
        "",
        "Mode: preview",
        "Safety: no GitHub comments were posted.",
        "",
        "| Issue | Title | Category | Answer Status | Reason | Lookup Mode | Evidence | Draft |",
        "|-------|-------|----------|---------------|--------|-------------|----------|-------|",
    ]
    for record in records:
        proposal = record.model_proposal
        answer_policy = record.answer_policy
        status = answer_policy.status if answer_policy is not None else "-"
        reason = (answer_policy.reason if answer_policy is not None else record.policy_decision.reason).replace("|", "\\|")
        evidence = _first_evidence(record)
        title = record.title.replace("|", "\\|")
        draft = record.draft_path or "-"
        lines.append(
            f"| #{record.issue_number} | {title} | {proposal.category} | {status} | "
            f"{reason} | {evidence['lookup_mode']} | {evidence['value']} | {draft} |"
        )
    lines.append("")
    return "\n".join(lines)


def _first_evidence(record: PreviewRecord) -> dict[str, str]:
    if not record.evidence_refs:
        return {"lookup_mode": "-", "value": "-"}
    ref = record.evidence_refs[0]
    return {
        "lookup_mode": ref.lookup_mode or "-",
        "value": (ref.path or ref.value or "-").replace("|", "\\|"),
    }
