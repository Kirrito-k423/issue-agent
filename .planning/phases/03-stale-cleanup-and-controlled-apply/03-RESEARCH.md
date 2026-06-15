# Phase 3 Research: Stale Cleanup and Controlled Apply

**Phase:** 3 - Stale Cleanup and Controlled Apply
**Researched:** 2026-06-15
**Status:** Complete

## Research Question

What does the executor need to know to plan Phase 3 well: linked issue/PR evidence extraction, conservative stale cleanup recommendations, and explicit apply mode for labels, comments, and closures?

## Inputs Read

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/03-stale-cleanup-and-controlled-apply/03-CONTEXT.md`
- `.planning/phases/01-core-preview-pipeline/01-CONTEXT.md`
- `.planning/phases/01-core-preview-pipeline/01-VERIFICATION.md`
- `.planning/phases/02-code-aware-triage-and-answers/02-CONTEXT.md`
- `.planning/phases/02-code-aware-triage-and-answers/02-VERIFICATION.md`
- `AGENTS.md`
- `skills/github-issue-close/SKILL.md`
- `issue_agent/models.py`
- `issue_agent/github.py`
- `issue_agent/classifier.py`
- `issue_agent/policy.py`
- `issue_agent/state.py`
- `issue_agent/preview.py`
- `issue_agent/cli.py`
- `examples/issues.fixture.json`
- `tests/test_github.py`
- `tests/test_state_preview.py`
- Local `gh issue close --help`, `gh issue comment --help`, and `gh issue edit --help`

## Key Findings

### 1. Closure policy needs structured linked evidence before age

The existing issue model already includes comments, labels, timestamps, and URLs. Phase 3 should start by extracting linked references from body and comments into structured records. Useful fields:

- repository and number
- kind: `issue`, `pull_request`, or `unknown`
- relation: duplicate, resolves, supersedes, blocks, mentions, waiting-for-info, or unknown
- source: body or comment index/author/timestamp
- status fields that a future resolver can fill: open, closed, merged, unresolved, unknown

Policy should then consume these records. Old timestamps alone should never drive `suitable_to_close=true`.

### 2. Conservative closure reasons map cleanly to policy outputs

The close skill and requirements point to five safe closure reasons:

- resolved by maintainer answer or merged fix
- duplicate of a still-valid canonical issue/PR/doc
- superseded or migrated to a better tracker
- unsupported or out of scope by maintainer decision
- stale waiting for requested information

Everything else should become `not_suitable`, `human_review`, or a high-risk preview. Roadmap/help-wanted/open contribution labels and open linked PRs should block closure recommendations unless explicit completion/supersession evidence exists.

### 3. Apply mode should validate preview records, not re-decide

Apply mode is a side-effect boundary. It should only execute action records that were already previewed. The safe shape is:

```text
close-preview -> records.json / pending-batch.json / latest-preview.md
apply --workflow close -> load preview record -> validate expected action -> execute adapter -> write result
```

No fresh model/policy decision should happen inside apply. This prevents drift between what the maintainer reviewed and what gets posted or closed.

### 4. GitHub mutation commands are narrow and adapter-friendly

Local GitHub CLI help confirms the required public mutations can be wrapped behind a runner:

- `gh issue comment {number|url} --body <text> --repo OWNER/REPO`
- `gh issue edit {number|url} --add-label <name> --repo OWNER/REPO`
- `gh issue edit {number|url} --remove-label <name> --repo OWNER/REPO`
- `gh issue close {number|url} --comment <text> --reason completed|not planned --repo OWNER/REPO`

Tests should not invoke these commands. Use a fake runner that records argv and can simulate failures.

### 5. State can follow the Phase 1/2 bounded pattern

Phase 1 and Phase 2 already established:

- canonical object records keyed by issue number
- pending batch overwritten per run
- latest Markdown preview overwritten per run
- no append-only local history

Phase 3 can add `close/` and `apply/` workflows under the configured state root. If action status must be tracked separately, use stable action ids such as `issue-5:add-label:stale` or `issue-5:close`.

## Recommended Plan Shape

### Plan 03-01: Linked Evidence Extraction

Add linked-reference models, parsing utilities, fixture cases, and status-ready evidence records for issue/PR references in bodies and comments.

### Plan 03-02: Closure Policy and Close Preview

Add closure recommendation models and policy, conservative fixture coverage, bounded close preview state, Markdown rendering, and a `close-preview` CLI command.

### Plan 03-03: Explicit Apply Engine

Add a GitHub mutation adapter, apply record models, preview-record validation, fake-runner tests, and an explicit apply CLI path for labels, comments, and closures.

## Validation Strategy

Phase 3 verification should prove:

- Linked references are extracted from issue body and comments into structured records.
- Old/help-wanted/roadmap/open-PR items are not recommended for closure solely because of age.
- Waiting-for-info and resolved/superseded fixture issues produce explainable close previews.
- Preview mode writes local state and never invokes mutation commands.
- Apply mode refuses missing or mismatched preview records.
- Apply mode records partial failures without retry loops and preserves preview evidence.
- Fake mutation tests prove command order and arguments without touching GitHub.
- Mutation-surface scan distinguishes preview paths from explicit apply paths.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Age becomes a hidden closure heuristic | Require explicit closure reason evidence and test old-but-not-closable fixtures. |
| Apply recomputes a different decision | Load and validate existing preview records only; no policy call in apply. |
| Partial apply failures hide state | Store one action result per label/comment/close action with status and error. |
| Tests touch real GitHub | All mutation tests use fake runners; CLI smoke can run preview only. |
| Open PRs get closed as stale | Treat open linked PR evidence as a closure blocker unless superseded. |

## Phase 3 File Targets

Likely implementation files:

- `issue_agent/links.py`
- `issue_agent/closure.py`
- `issue_agent/apply.py`
- `issue_agent/models.py`
- `issue_agent/classifier.py`
- `issue_agent/policy.py`
- `issue_agent/state.py`
- `issue_agent/preview.py`
- `issue_agent/github.py`
- `issue_agent/cli.py`
- `examples/issues.fixture.json`
- `tests/test_links.py`
- `tests/test_closure_policy.py`
- `tests/test_close_preview.py`
- `tests/test_apply.py`
- existing CLI/GitHub/state tests as needed

## Open Questions for Planning

None blocking. Exact enum names and file boundaries can be chosen during implementation as long as preview/apply separation, evidence-grounded closure, and bounded state are enforced.

## RESEARCH COMPLETE
