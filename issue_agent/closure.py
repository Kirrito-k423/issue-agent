from collections.abc import Iterable

from issue_agent.links import extract_linked_references
from issue_agent.models import ClosureDecision, IssueInput
from issue_agent.policy import evaluate_closure_policy


def build_closure_decisions(issues: Iterable[IssueInput], repo: str) -> list[ClosureDecision]:
    decisions: list[ClosureDecision] = []
    for issue in issues:
        linked_references = extract_linked_references(issue, repo)
        decisions.append(evaluate_closure_policy(issue, linked_references))
    return decisions


def build_close_preview_records(issues: Iterable[IssueInput], repo: str) -> list[ClosureDecision]:
    return build_closure_decisions(issues, repo)
