from collections.abc import Iterable

from issue_agent.models import ApplyResult, ClosureDecision, PreviewRecord, SummaryReport


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


def render_close_preview(records: Iterable[ClosureDecision]) -> str:
    lines = [
        "# Issue Agent Close Preview",
        "",
        "Mode: preview",
        "Safety: no GitHub issues were closed.",
        "",
        "| Issue | Suitable | Reason | Risk | Evidence | Draft |",
        "|-------|----------|--------|------|----------|-------|",
    ]
    for record in records:
        evidence = _first_closure_evidence(record)
        draft = "yes" if record.draft_comment else "-"
        lines.append(
            f"| #{record.issue_number} | {str(record.suitable_to_close).lower()} | "
            f"{record.closure_reason} | {record.risk_level} | {evidence} | {draft} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_apply_results(records: Iterable[ApplyResult]) -> str:
    lines = [
        "# Issue Agent Apply Results",
        "",
        "Mode: apply",
        "Safety: actions were requested explicitly after preview validation.",
        "",
        "| Action | Issue | Type | Status | Error |",
        "|--------|-------|------|--------|-------|",
    ]
    for record in records:
        error = (record.error or "-").replace("|", "\\|")
        lines.append(
            f"| {record.action_id} | #{record.issue_number} | {record.action_type} | "
            f"{record.status} | {error} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_summary_preview(report: SummaryReport) -> str:
    lines = [
        "# Issue Agent Summary Preview",
        "",
        "Mode: preview",
        "Safety: no GitHub issues were changed.",
        "",
        "| Workflow | Present | Records | Key Counts |",
        "|----------|---------|---------|------------|",
    ]
    for workflow in sorted(report.workflows):
        summary = report.workflows[workflow]
        counts = ", ".join(f"{key}={value}" for key, value in sorted(summary.counts.items())) or "-"
        safe_counts = counts.replace("|", "\\|")
        lines.append(
            f"| {summary.workflow} | {str(summary.present).lower()} | "
            f"{summary.total_records} | {safe_counts} |"
        )
    missing = ", ".join(report.missing_workflows) or "-"
    lines.extend(["", f"Missing workflows: {missing}", ""])
    return "\n".join(lines)


def _first_evidence(record: PreviewRecord) -> dict[str, str]:
    if not record.evidence_refs:
        return {"lookup_mode": "-", "value": "-"}
    ref = record.evidence_refs[0]
    return {
        "lookup_mode": ref.lookup_mode or "-",
        "value": (ref.path or ref.value or "-").replace("|", "\\|"),
    }


def _first_closure_evidence(record: ClosureDecision) -> str:
    if not record.evidence_refs:
        return "-"
    return record.evidence_refs[0].value.replace("|", "\\|")
