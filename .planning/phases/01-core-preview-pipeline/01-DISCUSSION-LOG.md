# Phase 1: Core Preview Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-15
**Phase:** 1-Core Preview Pipeline
**Areas discussed:** CLI and Project Shape, Configuration and Secrets, GitHub Intake, Model and Classification Boundary, Preview Safety and State, Phase 1 Scope Fence

---

## CLI and Project Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Python Typer CLI | Small Python package with explicit preview commands and fixture-backed tests. | yes |
| Shell-only scripts | Fastest prototype but harder to schema-test and extend. | |
| Import existing skills directly | Keeps prior text workflows but does not create a real executable system. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Phase 1 should establish the first executable implementation pattern.

---

## Configuration and Secrets

| Option | Description | Selected |
|--------|-------------|----------|
| YAML profiles plus env secrets | Track non-secret repo policy while keeping keys/tokens outside git. | yes |
| One local config with all values | Convenient but risks secret leakage. | |
| Hard-coded defaults only | Simple but blocks multi-repo use. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Include proxy-aware docs for `127.0.0.1:7890` without committing private machine credentials.

---

## GitHub Intake

| Option | Description | Selected |
|--------|-------------|----------|
| `gh` adapter first | Uses existing local auth and JSON output; isolate behind adapter. | yes |
| Direct REST first | More flexible but slower to build and authenticate in MVP. | |
| Fixture-only | Safe for tests but does not validate live workflow shape. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Tests must remain offline-safe; live network should be explicit.

---

## Model and Classification Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Pydantic schema plus provider interface | Model proposes, deterministic policy validates and downgrades. | yes |
| Free-form prompt output | Faster but unsafe for public issue automation. | |
| Provider-specific MiniMax code first | Useful later, but tests should not require live credentials. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Include deterministic fixture/mock provider in Phase 1.

---

## Preview Safety and State

| Option | Description | Selected |
|--------|-------------|----------|
| Preview-only Phase 1 | Write bounded local JSON/Markdown state; no GitHub mutation paths. | yes |
| Hidden apply flag early | Tempting but increases trust risk before policy is proven. | |
| Append-only logs | Easy history, but violates bounded state goal. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Preview records must show both model proposal and policy result.

---

## Phase 1 Scope Fence

| Option | Description | Selected |
|--------|-------------|----------|
| Reserve later fields but defer later workflows | Keep Phase 1 focused while leaving room for CodeGraph, answers, closure, and apply. | yes |
| Implement answer drafting now | Out of scope for core preview pipeline. | |
| Implement stale closure now | Too risky before evidence/policy foundations are built. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Existing `skills/` remain reference workflows, not executable baseline code.

## the agent's Discretion

- Exact Python module and helper names.
- Exact fixture data shape.
- Exact Markdown preview table layout.

## Deferred Ideas

- CodeGraph-backed answers in Phase 2.
- Stale cleanup and explicit apply mode in Phase 3.
- GitHub App auth, dashboarding, scheduling, and provider routing in v2.
