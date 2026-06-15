# Phase 3: Stale Cleanup and Controlled Apply - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 3 adds evidence-based stale cleanup recommendations and an explicit apply mode on top of the preview-first classifier and answer-preview pipeline. It should gather linked issue and PR evidence, decide whether closure is safe, write bounded close/apply preview records, and only perform GitHub label/comment/close mutations when apply mode is explicitly requested and a matching preview record already exists. This phase does not build aggregate reporting, dashboards, scheduled runs, GitHub App auth, or live model quality evaluation.

</domain>

<decisions>
## Implementation Decisions

### Linked Issue and PR Evidence
- **D-01:** Extract linked issue and PR references from issue body text and comments before making stale cleanup decisions. Supported references should include GitHub issue/PR URLs, `#123`, `owner/repo#123`, and common closing/supersession wording when present in local issue text.
- **D-02:** Represent linked references as structured evidence, not prose. Each reference should record repository, number, kind (`issue` or `pull_request` when known), relation, source field, and the evidence reason.
- **D-03:** The first implementation may stay fixture-backed, but it must make room for a GitHub status resolver that can later report linked PR state such as open, closed, or merged without changing policy semantics.
- **D-04:** Missing or unresolved linked-reference status must not be treated as closure evidence. Unknown linked state should increase risk or route the candidate to human review.

### Closure Recommendation Policy
- **D-05:** Never recommend closure solely because an issue or PR is old. Closure requires explicit evidence for one of the allowed reasons: resolved, duplicate, superseded, unsupported/out-of-scope, or stale waiting for requested information.
- **D-06:** Roadmap, help-wanted, good-first-issue, call-for-contribution, feature request, or active contribution items default to `not_suitable` unless there is clear completion, supersession, or maintainer decision evidence.
- **D-07:** Open linked PRs and active/recent discussion block automatic closure recommendations unless there is stronger evidence that the current item is no longer the right tracker.
- **D-08:** Close previews should include a risk level, closure reason, current state summary, evidence refs, and a draft close comment only when suitable to close.

### Controlled Apply Boundary
- **D-09:** Preview mode must remain unable to post comments, apply labels, or close issues. The code path for mutation must be behind an explicit apply command or explicit apply flag.
- **D-10:** Apply mode must require an existing matching preview record for the issue and action. It must not synthesize new closure decisions at apply time.
- **D-11:** Label changes, comments, and closures should be separate action records so partial failures are visible and do not erase preview evidence.
- **D-12:** Apply failures must preserve preview data, mark the failed action with status and error, and avoid retry loops.

### State and Fixture Strategy
- **D-13:** Reuse the bounded state convention from Phase 1 and Phase 2. Close/apply workflows should write canonical `records.json`, `pending-batch.json`, and `latest-preview.md` files, replacing records by issue number or action id instead of appending unbounded history.
- **D-14:** Extend existing models where natural, but keep closure policy and apply policy separate from answer policy so no public mutation can bypass the preview/apply boundary.
- **D-15:** Tests must remain offline and deterministic: use fixture issues/comments/linked refs and fake GitHub mutation runners rather than live `gh` calls.
- **D-16:** Verification must include a mutation-surface scan proving preview paths do not call `gh issue comment`, `gh issue edit`, or `gh issue close`.

### Phase 3 Scope Fence
- **D-17:** Do not implement aggregate summary reporting; that remains Phase 4.
- **D-18:** Do not introduce GitHub App auth, web dashboards, scheduling, or multi-repo operations; those remain v2.
- **D-19:** Do not create missing labels automatically. Apply mode may only use labels that already passed repository-label policy.
- **D-20:** Do not close roadmap/help-wanted/open-PR work by age; preserve the project rule that uncertainty means no public mutation.

### the agent's Discretion
- The agent may choose the exact names of closure/apply models and CLI commands as long as the commands are explicit and preview-first.
- The agent may initially classify linked PR/issue status from fixture metadata and leave live GitHub resolution behind an adapter.
- The agent may keep close comment wording simple and deterministic in Phase 3; safety and evidence boundaries matter more than prose style.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope and Requirements
- `.planning/PROJECT.md` — Core value, preview-first operation, CodeGraph rule, state constraints, and out-of-scope boundaries.
- `.planning/REQUIREMENTS.md` — Phase 3 requirement IDs `GH-03`, `SAFE-04`, `CLOSE-01` through `CLOSE-03`, and `APPLY-01` through `APPLY-04`.
- `.planning/ROADMAP.md` — Phase 3 goal, success criteria, and planned work breakdown.
- `.planning/STATE.md` — Current project position and completed Phase 1/2 context.

### Prior Phase Contracts
- `.planning/phases/01-core-preview-pipeline/01-CONTEXT.md` — Preview-state, schema, and mutation-safety decisions inherited by Phase 3.
- `.planning/phases/01-core-preview-pipeline/01-VERIFICATION.md` — Verified preview-only classification behavior.
- `.planning/phases/02-code-aware-triage-and-answers/02-CONTEXT.md` — Evidence-first and no-answer policy decisions inherited by stale cleanup.
- `.planning/phases/02-code-aware-triage-and-answers/02-VERIFICATION.md` — Verified answer-preview and no-public-comment behavior.

### Repository Instructions and Reference Workflows
- `AGENTS.md` — Chinese-first collaboration, proxy note, and CodeGraph-before-grep rule when `.codegraph/` exists.
- `skills/github-issue-close/SKILL.md` — Reference closure policy, Chinese current-state/decision shape, preview/apply separation, and bounded close records.
- `skills/github-issue-classify/SKILL.md` — Reference classification state and label safety boundary.
- `skills/github-issue-summary/SKILL.md` — Future Phase 4 reference only; do not implement summary output in Phase 3.

### Current Implementation
- `issue_agent/models.py` — Existing issue, evidence, classifier, policy, answer-policy, preview-record, and batch-preview schemas.
- `issue_agent/github.py` — Fixture issue/label loaders and placeholder live GitHub client.
- `issue_agent/classifier.py` — Fixture classifier categories including `stale_cleanup_candidate`.
- `issue_agent/policy.py` — Deterministic policy enforcement pattern.
- `issue_agent/state.py` — Bounded state writer patterns.
- `issue_agent/preview.py` — Markdown preview rendering patterns.
- `issue_agent/cli.py` — Typer CLI entrypoint and explicit preview commands.
- `examples/issues.fixture.json` — Fixture batch to extend with stale/linked cleanup cases.
- `tests/test_github.py` — Fixture intake tests.
- `tests/test_state_preview.py` — Bounded state replacement tests.
- `tests/test_cli_skeleton.py` — CLI fixture smoke pattern.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `IssueInput.comments` already carries comment bodies and timestamps, enough to fixture linked-reference parsing without live GitHub calls.
- `EvidenceRef` already supports path/snippet/lookup metadata; Phase 3 can reuse it for issue/comment/PR evidence and add closure-specific models where needed.
- `PreviewRecord.github_mutation_applied` is the existing safety flag; apply records should make mutation status explicit without weakening that invariant.
- `write_batch_preview` and `write_answer_preview` show the bounded-state pattern for canonical records, pending batch, latest preview, and optional draft files.

### Established Patterns
- CLI commands are explicit (`preview`, `answer-preview`) and announce preview safety in stdout.
- Tests use deterministic fixtures and fake providers/runners; no live GitHub or model calls are required for verification.
- Policy modules decide safety deterministically before any user-facing draft or mutation action exists.
- Planning artifacts use requirement IDs and GSD verification gates to prove coverage.

### Integration Points
- Linked-reference extraction connects to issue intake before stale policy.
- Closure policy consumes issue metadata, labels, comments, linked evidence, and existing preview state.
- Close/apply state should live beside existing workflows under the configured `state_root`.
- Apply mode should call a narrow GitHub mutation adapter only after preview record validation.

</code_context>

<specifics>
## Specific Ideas

- Use a fixture issue that is old but `help wanted` or has an open PR to prove "old alone is not enough."
- Use a fixture issue with a maintainer "please provide reproduction" comment and no later author reply to prove `stale_waiting_for_info`.
- Use fake mutation runners in tests to prove apply order and failure recording without touching GitHub.
- Keep close previews readable in Markdown, with columns for issue, suitable, reason, risk, evidence, and draft/action path.

</specifics>

<deferred>
## Deferred Ideas

- Aggregate classification/answer/closure reporting remains Phase 4.
- Live GitHub App auth, dashboards, scheduling, multi-repo orchestration, and provider cost evaluation remain v2.
- Polished bilingual close-comment style can improve later; Phase 3 only needs deterministic, respectful, evidence-cited draft text.

</deferred>

---

*Phase: 3-Stale Cleanup and Controlled Apply*
*Context gathered: 2026-06-15*
