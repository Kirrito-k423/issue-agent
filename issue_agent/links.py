import re

from issue_agent.models import IssueInput, LinkedReference, LinkedReferenceKind, LinkedReferenceRelation


_GITHUB_URL_RE = re.compile(
    r"https?://github\.com/(?P<repo>[\w.-]+/[\w.-]+)/(?:issues|pull)/(?P<number>\d+)"
)
_GITHUB_URL_KIND_RE = re.compile(r"github\.com/[\w.-]+/[\w.-]+/(?P<kind>issues|pull)/\d+")
_CROSS_REPO_RE = re.compile(r"(?<![\w./-])(?P<repo>[\w.-]+/[\w.-]+)#(?P<number>\d+)")
_SHORT_REF_RE = re.compile(r"(?<![\w/.-])#(?P<number>\d+)")


def extract_linked_references(issue: IssueInput, default_repo: str) -> list[LinkedReference]:
    references: list[LinkedReference] = []
    seen: set[tuple[str, int, str, str]] = set()

    for reference in _extract_from_text(issue.body, "body", default_repo):
        _append_unique(references, seen, reference)

    for index, comment in enumerate(issue.comments):
        source = f"comment:{index}"
        for reference in _extract_from_text(comment.body, source, default_repo):
            _append_unique(references, seen, reference)

    return references


def _extract_from_text(text: str, source: str, default_repo: str) -> list[LinkedReference]:
    references: list[LinkedReference] = []

    for match in _GITHUB_URL_RE.finditer(text):
        url = match.group(0)
        references.append(
            LinkedReference(
                repository=match.group("repo"),
                number=int(match.group("number")),
                kind=_kind_from_url(url),
                relation=_infer_relation(text, match.start(), match.end()),
                source=source,
                reason=f"{source} links to {url}.",
                url=url,
            )
        )

    masked = _GITHUB_URL_RE.sub("", text)
    for match in _CROSS_REPO_RE.finditer(masked):
        references.append(
            LinkedReference(
                repository=match.group("repo"),
                number=int(match.group("number")),
                kind="unknown",
                relation=_infer_relation(masked, match.start(), match.end()),
                source=source,
                reason=f"{source} mentions {match.group(0)}.",
            )
        )

    masked = _CROSS_REPO_RE.sub("", masked)
    for match in _SHORT_REF_RE.finditer(masked):
        references.append(
            LinkedReference(
                repository=default_repo,
                number=int(match.group("number")),
                kind="unknown",
                relation=_infer_relation(masked, match.start(), match.end()),
                source=source,
                reason=f"{source} mentions {match.group(0)}.",
            )
        )

    return references


def _append_unique(
    references: list[LinkedReference],
    seen: set[tuple[str, int, str, str]],
    reference: LinkedReference,
) -> None:
    key = (reference.repository, reference.number, reference.kind, reference.source)
    if key not in seen:
        references.append(reference)
        seen.add(key)


def _kind_from_url(url: str) -> LinkedReferenceKind:
    match = _GITHUB_URL_KIND_RE.search(url)
    if match is None:
        return "unknown"
    return "pull_request" if match.group("kind") == "pull" else "issue"


def _infer_relation(text: str, start: int, end: int) -> LinkedReferenceRelation:
    window = text[max(0, start - 160) : min(len(text), end + 160)].lower()
    if "duplicate" in window or "dupe" in window:
        return "duplicate"
    if "supersed" in window or "replaced by" in window or "migrated to" in window:
        return "superseded_by"
    if "resolve" in window or "resolved" in window or "fixed by" in window or "closed by" in window:
        return "resolved_by"
    if "block" in window:
        return "blocked_by"
    if "waiting for" in window or "please provide" in window or "need more information" in window:
        return "waiting_for_info"
    return "mentions"
