# Phase 2: Code-Aware Triage and Answers - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 extends the preview-only issue pipeline so it can separate code questions from unverified reproduction or environment requests, gather source evidence from the target repository, and write answer-preview records only when evidence supports a draft. This phase implements CodeGraph-first lookup and fallback evidence recording, no-answer gates for experiment and environment issues, and source-backed answer drafts. It does not post comments, close issues, mutate labels, or implement stale cleanup apply mode.

</domain>

<decisions>
## Implementation Decisions

### CodeGraph-First Evidence Lookup
- **D-01:** Add a source lookup adapter that checks the target repository root for `.codegraph/` before using any grep, `rg`, or direct file search for code-question evidence.
- **D-02:** When `.codegraph/` exists, the adapter should run CodeGraph first through shell commands such as `codegraph explore "<query>"` and `codegraph node <symbol-or-file>`. Downstream implementation may wrap these commands, but the observable lookup mode must remain `codegraph`.
- **D-03:** When CodeGraph is missing, unavailable, or fails, fallback lookup is allowed, but every preview record must explicitly record the fallback mode and reason so the answer is not presented as CodeGraph-backed.
- **D-04:** Source evidence records should be structured, not free-form strings. Each record should include repository-relative path, optional symbol, snippet or line reference when available, lookup mode, relevance reason, and any fallback/error note.

### No-Answer Gates
- **D-05:** Experiment, hardware, dependency, install, and environment reproduction issues require explicit run evidence before any answer draft can be produced.
- **D-06:** If the agent cannot run or verify the requested environment, policy should produce a preview-safe no-answer decision such as `human_review`, `request_info`, or `blocked`, with a clear reason like `requires_unverified_reproduction`.
- **D-07:** These no-answer gates should run deterministically before drafting, so a simple model cannot bypass them by proposing confident prose.
- **D-08:** Under uncertainty, keep the existing Phase 1 rule: no public mutation, no invented labels, and no unsupported answer.

### Answer Drafting and Reply-Worthiness
- **D-09:** Code logic answers require at least one source evidence record before a draft reply is generated.
- **D-10:** Usage questions may produce drafts from issue or documentation evidence, but the preview record must still cite the evidence used. If no evidence exists, skip drafting and record why.
- **D-11:** Reply-worthiness must be evaluated separately from text generation. The system should first decide whether a reply is supportable, then draft only for supportable issues.
- **D-12:** Draft replies remain preview-only in Phase 2 and should be stored as local preview artifacts. Comment posting remains out of scope until explicit apply mode in a later phase.

### State and CLI Integration
- **D-13:** Extend the existing Phase 1 schemas rather than replacing them. `PreviewRecord`, `EvidenceRef`, and `PolicyDecision` are the natural integration points.
- **D-14:** Add a dedicated answer-preview workflow under bounded state, likely `answer/records.json`, `answer/pending-batch.json`, `answer/latest-preview.md`, and per-issue draft files when useful.
- **D-15:** Keep fixture-backed tests as the primary verification path. Tests must cover CodeGraph-present behavior through a stubbed command runner or fixture directory, fallback mode when `.codegraph/` is absent, no-answer behavior for reproduction-only issues, and missing-evidence skips for code questions.
- **D-16:** The CLI should remain explicit and preview-first. New commands may be added for answer preview, but they must not expose `gh issue comment`, closure, or apply behavior in this phase.

### Phase 2 Scope Fence
- **D-17:** Do not implement stale issue or PR cleanup in Phase 2; that remains Phase 3.
- **D-18:** Do not implement public GitHub comment posting, label application, or closure in Phase 2.
- **D-19:** Do not require a live MiniMax or GitHub call for tests. Provider behavior should remain deterministic or fixture-backed unless the user explicitly opts into live mode.
- **D-20:** Do not index this repository with CodeGraph as part of the phase. The adapter should respect `.codegraph/` when it exists in a target repository, but indexing is an operator decision.

### the agent's Discretion
- The agent may choose exact module names, command names, and draft file layout as long as preview-only state remains bounded and evidence is visible.
- The agent may choose whether fallback source search is initially minimal or richer, provided fallback mode is recorded and tests prove no answer is drafted without evidence.
- The agent may defer polished natural-language reply style if the first implementation proves the safety gates and evidence plumbing.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope and Requirements
- `.planning/PROJECT.md` — Core value, constraints, CodeGraph-first rule, and preview-first mutation policy.
- `.planning/REQUIREMENTS.md` — Phase 2 requirement IDs `CODE-01` through `CODE-04`, `SAFE-01`, `SAFE-02`, and `ANS-01` through `ANS-03`.
- `.planning/ROADMAP.md` — Phase 2 goal, success criteria, and planned work breakdown.
- `.planning/STATE.md` — Current project position and active concerns.
- `.planning/phases/01-core-preview-pipeline/01-CONTEXT.md` — Phase 1 decisions that constrain schemas, preview state, and safety behavior.
- `.planning/phases/01-core-preview-pipeline/01-VERIFICATION.md` — Confirmed Phase 1 behavior and verification scope.

### Repository Instructions and Reference Workflows
- `AGENTS.md` — Chinese-first collaboration, proxy note, and CodeGraph-before-grep rule when `.codegraph/` exists.
- `skills/github-issue-reply/SKILL.md` — Reference for reply-worthiness separation, preview-before-comment behavior, and evidence-based replies.
- `skills/github-issue-classify/SKILL.md` — Reference for bounded classification state and preview/apply separation.
- `skills/github-issue-close/SKILL.md` — Reference for conservative no-action behavior; closure itself remains out of scope.

### Current Implementation
- `issue_agent/models.py` — Existing schemas for issue input, classifier proposals, policy decisions, evidence refs, preview records, and batch previews.
- `issue_agent/classifier.py` — Existing provider boundary and deterministic fixture classifier.
- `issue_agent/policy.py` — Existing deterministic policy enforcement point.
- `issue_agent/state.py` — Existing bounded state writer for preview workflows.
- `issue_agent/preview.py` — Existing Markdown preview rendering pattern.
- `issue_agent/cli.py` — Existing Typer CLI entrypoint and preview command.
- `tests/test_classifier_policy.py` — Existing schema and policy test style.
- `tests/test_state_preview.py` — Existing bounded state verification.
- `tests/test_cli_skeleton.py` — Existing CLI end-to-end fixture test.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `issue_agent.models.EvidenceRef`: currently generic; should be extended or complemented with source-specific fields for lookup mode, path, symbol, snippet, and relevance reason.
- `issue_agent.models.PreviewRecord`: already carries `evidence_refs` and `github_mutation_applied`; Phase 2 can add answer and no-answer fields without changing the preview-first boundary.
- `issue_agent.policy.apply_policy`: central deterministic gate for downgrading unsupported outputs; Phase 2 should add no-answer and missing-evidence rules here or in a nearby policy module.
- `issue_agent.state.write_batch_preview`: already supports bounded workflow-specific state roots; Phase 2 can reuse it for an `answer` workflow or add a sibling writer for draft files.
- `issue_agent.cli.preview`: existing Typer command proves the fixture-first end-to-end path and should guide new answer-preview commands.

### Established Patterns
- The model proposes; deterministic Python policy decides what is safe to preview.
- Fixture-backed tests are first-class and should not require live GitHub, live model credentials, CodeGraph installation, or network.
- Preview records are canonical JSON entries keyed by issue number and are replaced on reprocessing.
- Markdown previews summarize decisions for humans while JSON remains the machine-readable source of truth.

### Integration Points
- Source lookup should connect after classification identifies `code_logic_question` or `usage_question`, before any answer draft is considered.
- No-answer policy should consume classifier category, issue text, evidence needs, and available source/run evidence.
- Answer preview should reuse the current state-root convention and keep generated draft bodies local.
- CodeGraph command execution should be isolated behind an adapter so later live repository checkout handling, remote execution, and provider routing do not leak into policy or preview rendering.

</code_context>

<specifics>
## Specific Ideas

- Treat CodeGraph availability as target-repository evidence, not a requirement for this repository itself.
- Record fallback mode prominently in both JSON and Markdown preview output so reviewers can tell whether a draft was CodeGraph-backed, shell-search-backed, or skipped.
- Use conservative reasons such as `missing_source_evidence`, `requires_unverified_reproduction`, and `unsupported_environment_claim` to make skipped answers auditable.
- Keep Phase 2 answer drafts short, evidence-cited, and local. Style polish can improve later, but unsupported answers must be impossible now.

</specifics>

<deferred>
## Deferred Ideas

- Stale cleanup, closure recommendations, linked PR/issue evidence extraction, and GitHub apply mode remain Phase 3.
- Aggregate summary reporting and broader regression fixture suites remain Phase 4.
- Live provider quality evaluation, multi-repo scheduling, and dashboards remain v2 work.

</deferred>

---

*Phase: 2-Code-Aware Triage and Answers*
*Context gathered: 2026-06-15*
