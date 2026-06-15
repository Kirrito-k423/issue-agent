import json
from collections.abc import Callable, Iterable
from typing import Protocol

from pydantic import ValidationError

from issue_agent.models import ClassifierProposal, IssueInput, PolicyDecision


class ClassifierProvider(Protocol):
    def classify(self, issue: IssueInput) -> ClassifierProposal:
        ...


class FixtureClassifierProvider:
    def classify(self, issue: IssueInput) -> ClassifierProposal:
        text = f"{issue.title}\n{issue.body}".lower()
        category = "unknown_unsafe"
        labels: list[str] = []
        evidence_needs: list[str] = ["human_review"]
        proposed_action = "no_public_action"
        reason = "No safe fixture signal matched this issue."

        if _contains_any(
            text,
            ["reproduce", "reproduction", "environment", "hardware", "dependency", "cuda", "npu", "install"],
        ):
            category = "experiment_reproduction"
            labels = ["bug"]
            evidence_needs = ["run_evidence"]
            proposed_action = "request_info"
            reason = "The fixture issue requires environment or reproduction evidence."
        elif _contains_any(text, ["source", "code", "function", "implementation", "logic", "where is"]):
            category = "code_logic_question"
            labels = ["question"]
            evidence_needs = ["source_evidence"]
            proposed_action = "preview_answer"
            reason = "The fixture issue asks about repository code behavior."
        elif _contains_any(text, ["how", "question", "can i", "is it possible", "?"]):
            category = "usage_question"
            labels = ["question"]
            evidence_needs = []
            proposed_action = "preview_classification"
            reason = "The fixture issue asks a usage or behavior question."
        elif _contains_any(text, ["bug", "invalid", "malformed", "error", "failure", "crash"]):
            category = "bug_report"
            labels = ["bug"]
            evidence_needs = []
            proposed_action = "preview_classification"
            reason = "The fixture issue describes invalid or failing behavior."
        elif _contains_any(text, ["feature", "enhancement", "support", "improve"]):
            category = "feature_enhancement"
            labels = ["enhancement"]
            evidence_needs = []
            proposed_action = "preview_classification"
            reason = "The fixture issue asks for a feature or improvement."

        return ClassifierProposal(
            category=category,
            confidence=0.75 if labels else 0.2,
            proposed_action=proposed_action,
            evidence_needs=evidence_needs,
            no_action_reason=None if labels else "No deterministic fixture signal matched.",
            labels_proposed=labels,
            reason=reason,
        )


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    return any(needle in text for needle in needles)


def parse_or_human_review(raw: str, repair: Callable[[str], str] | None = None) -> ClassifierProposal | PolicyDecision:
    try:
        return ClassifierProposal.model_validate(json.loads(raw))
    except (json.JSONDecodeError, ValidationError, TypeError):
        if repair is not None:
            try:
                return ClassifierProposal.model_validate(json.loads(repair(raw)))
            except (Exception,):
                pass
    return PolicyDecision(
        labels_applyable=[],
        labels_rejected=[],
        status="human_review",
        reason="invalid_classifier_output",
    )
