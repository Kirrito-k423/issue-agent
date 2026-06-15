# Phase 3: Stale Cleanup and Controlled Apply - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-15
**Phase:** 3-Stale Cleanup and Controlled Apply
**Areas discussed:** linked issue and PR evidence, closure recommendation policy, controlled apply boundary, state and fixture strategy

---

## Linked Issue and PR Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Structured linked-reference extraction | Parse issue body/comments for issue and PR references, record relation and source field. | ✓ |
| Prose-only summary | Let closure policy read free-form comment summaries without structured refs. | |
| Live GitHub-only resolution | Require live `gh` status resolution before any fixture support. | |

**User's choice:** [auto] Structured linked-reference extraction.
**Notes:** Recommended because Phase 3 must prove evidence grounding offline first, while preserving a future live GitHub adapter.

---

## Closure Recommendation Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Conservative evidence-gated closure | Closure requires resolved, duplicate, superseded, unsupported, or waiting-info evidence. | ✓ |
| Age-weighted stale closure | Old issues become closure candidates unless blocked by recent activity. | |
| Human-only closure | Generate no closure recommendations in code. | |

**User's choice:** [auto] Conservative evidence-gated closure.
**Notes:** This matches the project rule that age alone is insufficient and roadmap/help-wanted/open-PR issues must stay open unless clear evidence says otherwise.

---

## Controlled Apply Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit apply after matching preview | Mutations require an explicit apply command/flag and existing preview record. | ✓ |
| Apply from fresh policy evaluation | Recompute closure decisions at apply time. | |
| Preview only forever | Do not implement mutation commands in Phase 3. | |

**User's choice:** [auto] Explicit apply after matching preview.
**Notes:** The roadmap requires controlled apply mode, but apply must not bypass preview evidence.

---

## State and Fixture Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Bounded close/apply state with fixture tests | Reuse records/pending/preview state shape and fake mutation runners. | ✓ |
| Append-only audit log | Keep every run forever in JSONL. | |
| Live GitHub integration-first | Verify mainly against real GitHub calls. | |

**User's choice:** [auto] Bounded close/apply state with fixture tests.
**Notes:** Keeps Phase 3 aligned with Phase 1/2 deterministic verification and avoids leaking public side effects into tests.

---

## the agent's Discretion

- Exact model names and CLI command names are left to the planner/executor as long as they are explicit and preview-first.
- Close comment wording can be simple and deterministic.

## Deferred Ideas

- Aggregate reporting and polished summary output remain Phase 4.
- GitHub App auth, dashboards, scheduling, and multi-repo operations remain v2.
