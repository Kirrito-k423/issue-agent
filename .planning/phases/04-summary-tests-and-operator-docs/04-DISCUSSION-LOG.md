# Phase 4: Summary, Tests, and Operator Docs - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-16
**Phase:** 04-summary-tests-and-operator-docs
**Areas discussed:** Aggregate summary shape, regression fixture coverage, operator documentation, secret and state hygiene

---

## Aggregate Summary Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Local preview aggregation | Read existing state files and write bounded JSON plus Markdown under `summary/`. | ✓ |
| Live recomputation | Re-run classifier, answer, and closure policy while summarizing. | |
| External dashboard | Build a hosted or browser dashboard. | |

**User's choice:** Auto-selected local preview aggregation.
**Notes:** Matches project core value: summarize existing evidence without creating new decisions or mutations.

---

## Regression Fixture Coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Offline end-to-end fixture path | Use fixture issues, temp state, and fake runners across classify/answer/close/apply/summary. | ✓ |
| Live GitHub smoke tests | Exercise real GitHub CLI calls in tests. | |
| Snapshot-heavy Markdown tests | Snapshot full rendered Markdown files. | |

**User's choice:** Auto-selected offline end-to-end fixture path.
**Notes:** Keeps tests deterministic and safe on the China-based Mac or remote servers with intermittent network.

---

## Operator Documentation

| Option | Description | Selected |
|--------|-------------|----------|
| README plus operator guide | Keep README short and add `docs/` guide for full workflow and safety boundaries. | ✓ |
| README only | Put all details in the root README. | |
| Generated site | Create a hosted or static documentation site. | |

**User's choice:** Auto-selected README plus operator guide.
**Notes:** The guide can cover proxy, CodeGraph, preview/apply, and remote-server notes without bloating quickstart.

---

## Secret and State Hygiene

| Option | Description | Selected |
|--------|-------------|----------|
| Lightweight tracked-file scan | Add verification for obvious tokens, private paths, and generated state leakage. | ✓ |
| Manual review only | Rely on human review of docs and examples. | |
| Secret scanner dependency | Add a new third-party scanner. | |

**User's choice:** Auto-selected lightweight tracked-file scan.
**Notes:** Avoids new dependencies while covering the project-specific leakage risks.

---

## the agent's Discretion

- Exact summary model/helper names.
- Whether summary logic is in a new module or near state/preview helpers.
- Exact test-file split as long as the safety invariants are covered.

## Deferred Ideas

- Dashboard, recurring automation, GitHub App auth, multi-repo scheduling, and provider quality dashboards remain v2.
