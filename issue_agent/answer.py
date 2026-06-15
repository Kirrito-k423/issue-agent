from collections.abc import Callable, Iterable, Sequence
from pathlib import Path

from issue_agent.classifier import ClassifierProvider
from issue_agent.codegraph import lookup_source_evidence
from issue_agent.models import EvidenceRef, IssueInput, PolicyDecision, PreviewRecord
from issue_agent.policy import evaluate_answer_policy


SourceLookup = Callable[[Path, str], list[EvidenceRef]]


def build_answer_preview_records(
    issues: Iterable[IssueInput],
    repo_root: Path,
    classifier: ClassifierProvider,
    source_lookup: SourceLookup = lookup_source_evidence,
) -> list[PreviewRecord]:
    records: list[PreviewRecord] = []
    for issue in issues:
        proposal = classifier.classify(issue)
        evidence_refs = _collect_answer_evidence(issue, repo_root, proposal.category, source_lookup)
        source_refs = [ref for ref in evidence_refs if ref.kind == "source"]
        answer_policy = evaluate_answer_policy(
            issue,
            proposal,
            source_evidence=source_refs,
            run_evidence=[],
        )
        records.append(
            PreviewRecord(
                issue_number=issue.number,
                title=issue.title,
                model_proposal=proposal,
                policy_decision=PolicyDecision(
                    labels_applyable=[],
                    labels_rejected=[],
                    status="preview_ready" if answer_policy.reply_worthy else "human_review",
                    reason=answer_policy.reason,
                ),
                answer_policy=answer_policy,
                evidence_refs=evidence_refs,
                draft_path=None,
                github_mutation_applied=False,
            )
        )
    return records


def _collect_answer_evidence(
    issue: IssueInput,
    repo_root: Path,
    category: str,
    source_lookup: SourceLookup,
) -> list[EvidenceRef]:
    if category == "code_logic_question":
        return source_lookup(repo_root, _issue_query(issue))
    if category == "usage_question":
        return [
            EvidenceRef(
                kind="issue",
                value=issue.url,
                reason="Issue text provides usage-question context.",
            )
        ]
    return []


def _issue_query(issue: IssueInput) -> str:
    return " ".join(part for part in [issue.title, issue.body] if part)
