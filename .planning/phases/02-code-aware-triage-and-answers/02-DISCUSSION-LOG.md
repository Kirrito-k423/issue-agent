# Phase 2: Code-Aware Triage and Answers - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-15
**Phase:** 2-Code-Aware Triage and Answers
**Areas discussed:** CodeGraph evidence path, no-answer gates, answer drafting and reply-worthiness, state and CLI integration

---

## CodeGraph Evidence Path

| Option | Description | Selected |
|--------|-------------|----------|
| CodeGraph-first adapter | Detect `.codegraph/`, run CodeGraph before fallback search, and record lookup mode in evidence. | ✓ |
| Generic search only | Use `rg`/file reads for all code questions and treat CodeGraph as optional future optimization. | |
| Require CodeGraph always | Skip source lookup entirely unless CodeGraph is installed and indexed. | |

**User's choice:** Auto-selected recommended default.
**Notes:** This follows the project rule that CodeGraph is primary when a target repo has `.codegraph/`, while keeping fallback mode auditable when CodeGraph is absent.

---

## No-Answer Gates

| Option | Description | Selected |
|--------|-------------|----------|
| Deterministic gate before drafting | Block experiment, hardware, dependency, and environment answers unless run evidence exists. | ✓ |
| Let model decide | Ask the model whether enough evidence exists and rely on confidence. | |
| Draft with caveats | Generate cautious prose even when the agent has not verified the environment. | |

**User's choice:** Auto-selected recommended default.
**Notes:** This captures the user's original constraint: concrete experiment issues with no environment reproduction should not be answered.

---

## Answer Drafting and Reply-Worthiness

| Option | Description | Selected |
|--------|-------------|----------|
| Evidence-gated draft previews | First decide reply-worthiness, then draft only when source or doc evidence exists. | ✓ |
| Draft every code question | Always produce a draft and let the maintainer judge evidence quality later. | |
| Classification only | Defer answer drafting entirely to a later phase. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Code logic questions should get useful source-backed previews, but missing evidence must skip drafting rather than produce speculative text.

---

## State and CLI Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Extend Phase 1 preview state | Reuse schemas, policy, state writer, and fixture CLI patterns for answer preview. | ✓ |
| Separate answer subsystem | Create an independent answer pipeline with separate models and state logic. | |
| Live-first command | Optimize the command for live GitHub/model calls before fixture coverage. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Phase 1 already established the safe preview skeleton. Extending it keeps blast radius small and preserves offline verification.

---

## the agent's Discretion

- Exact module names, command names, and answer draft file layout.
- Whether fallback source search starts with minimal file reads or richer symbol heuristics.
- How polished the first answer draft prose should be, as long as the evidence gate is enforced.

## Deferred Ideas

- Stale cleanup and closure recommendation logic are deferred to Phase 3.
- GitHub comment posting and other public mutations are deferred to explicit apply mode.
- Aggregate summary reporting is deferred to Phase 4.
