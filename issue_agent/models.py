from typing import Literal

from pydantic import BaseModel, Field


IssueCategory = Literal[
    "experiment_reproduction",
    "code_logic_question",
    "usage_question",
    "stale_cleanup_candidate",
    "feature_enhancement",
    "bug_report",
    "unknown_unsafe",
]

SourceLookupMode = Literal["codegraph", "fallback_search", "unavailable"]


class IssueComment(BaseModel):
    author: str
    body: str
    created_at: str


class IssueInput(BaseModel):
    number: int
    title: str
    body: str
    labels: list[str] = Field(default_factory=list)
    author: str
    url: str
    created_at: str
    updated_at: str
    comments: list[IssueComment] = Field(default_factory=list)


class LabelInfo(BaseModel):
    name: str
    description: str | None = None


class EvidenceRef(BaseModel):
    kind: str
    value: str
    reason: str
    lookup_mode: SourceLookupMode | None = None
    path: str | None = None
    symbol: str | None = None
    snippet: str | None = None
    line_start: int | None = Field(default=None, ge=1)
    line_end: int | None = Field(default=None, ge=1)
    codegraph_available: bool | None = None
    fallback_reason: str | None = None


class ClassifierProposal(BaseModel):
    category: IssueCategory
    confidence: float = Field(ge=0.0, le=1.0)
    proposed_action: str
    evidence_needs: list[str] = Field(default_factory=list)
    no_action_reason: str | None = None
    labels_proposed: list[str] = Field(default_factory=list)
    reason: str


class LabelRejection(BaseModel):
    name: str
    reason: str


class PolicyDecision(BaseModel):
    labels_applyable: list[str] = Field(default_factory=list)
    labels_rejected: list[LabelRejection] = Field(default_factory=list)
    status: Literal["preview_ready", "human_review", "blocked"] = "preview_ready"
    reason: str


class AnswerPolicyDecision(BaseModel):
    reply_worthy: bool
    status: Literal["draft_ready", "request_info", "human_review", "blocked", "skipped"]
    reason: str
    required_evidence: list[str] = Field(default_factory=list)
    draft_path: str | None = None


class PreviewRecord(BaseModel):
    issue_number: int
    title: str
    model_proposal: ClassifierProposal
    policy_decision: PolicyDecision
    answer_policy: AnswerPolicyDecision | None = None
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    draft_path: str | None = None
    github_mutation_applied: bool = False


class BatchPreview(BaseModel):
    mode: Literal["preview"] = "preview"
    workflow: str
    records: list[PreviewRecord] = Field(default_factory=list)
