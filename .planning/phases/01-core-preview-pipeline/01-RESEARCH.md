# Phase 1 Research: Core Preview Pipeline

**Phase:** 1 - Core Preview Pipeline
**Researched:** 2026-06-15
**Status:** Complete

## Research Question

What does the executor need to know to plan Phase 1 well: a safe first vertical slice that loads config, reads or fetches issue data, validates classifier proposals, and writes bounded preview artifacts without mutating GitHub?

## Inputs Read

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/01-core-preview-pipeline/01-CONTEXT.md`
- `.planning/research/SUMMARY.md`
- `.planning/research/STACK.md`
- `.planning/research/ARCHITECTURE.md`
- `.planning/research/PITFALLS.md`
- `AGENTS.md`
- `skills/github-issue-classify/SKILL.md`

## Key Findings

### 1. Build the first slice around a fixture-safe CLI

Phase 1 should not begin with live model or live GitHub dependencies. The first executable slice should run offline from a fixture issue batch, produce deterministic classifier proposals, and write preview state. This proves the core orchestration path while keeping tests stable and safe.

The thin path is:

```text
example config -> fixture issue batch -> classifier proposal schema -> policy validation -> records.json/pending-batch.json/latest-preview.md
```

### 2. Keep GitHub behind an adapter from the start

`gh` should be the default live integration, but the workflow must not spread subprocess calls through the codebase. Use one adapter boundary that can load fixture JSON for tests and use `gh` for live operations later.

Phase 1 only needs enough live shape to prove commands and JSON parsing; tests should exercise fixtures.

### 3. Model output must be schema-first

Pydantic schemas should exist before provider calls. The executor should define these separately:

- `IssueInput`
- `LabelInfo`
- `EvidenceRef`
- `ClassifierProposal`
- `PolicyDecision`
- `PreviewRecord`
- `BatchPreview`

The model provider returns proposals; policy decides whether labels are valid, missing, or unsafe.

### 4. Preview mode is a hard safety boundary

Phase 1 must not include any public mutation command path. There should be no implementation that calls:

- `gh issue edit`
- `gh issue comment`
- `gh issue close`
- label creation endpoints

The CLI can mention apply as future work in help/docs, but no apply flag should perform mutation in Phase 1.

### 5. State should stay bounded and git-ignored

Use the historical skill state shape as a reference, but simplify it for Phase 1:

- `records.json`: object keyed by issue number string
- `pending-batch.json`: current batch preview
- `latest-preview.md`: human-readable batch summary

Generated state belongs under `.issue-agent/state/<owner>__<repo>/classify/`, which is already ignored by `.gitignore`.

## Recommended Plan Shape

### Plan 01-01: CLI Walking Skeleton

Create project scaffolding, config loading, a deterministic fixture provider, and one command that writes preview artifacts from static fixture data. This proves the end-to-end path without live GitHub or model calls.

### Plan 01-02: GitHub Intake and Labels

Add the GitHub adapter, label loading, issue intake models, and fixture/live separation. Keep live commands explicit and tests fixture-based.

### Plan 01-03: Classifier Schema, Policy, and State Hardening

Replace the earliest skeleton proposal path with full Pydantic schemas, mock/model provider interface, policy validation, invalid-output handling, absent-label rejection, and stronger preview records.

## Validation Strategy

Phase 1 verification should prove:

- `pytest` passes without network or provider credentials.
- A fixture command writes `records.json`, `pending-batch.json`, and `latest-preview.md`.
- Generated preview records include model proposal and policy result.
- Missing labels become rejected/non-applyable, not created.
- Preview commands contain no reachable GitHub mutation path.
- Secrets are not written to config examples, state, preview, or docs.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Executor builds horizontal layers only | Plans must start with a runnable fixture preview command and refine it. |
| Live GitHub calls make tests flaky | Fixtures are the default for tests; live mode is explicit. |
| Model output validation is postponed | Define Pydantic schemas before provider-specific calls. |
| Preview mode accidentally mutates GitHub | Phase 1 excludes all edit/comment/close/apply paths and tests for that absence. |
| State files are committed accidentally | `.issue-agent/state/` remains ignored; tests should use temporary directories. |

## Phase 1 File Targets

Likely implementation files:

- `pyproject.toml`
- `README.md`
- `.env.example`
- `examples/config.yaml`
- `examples/issues.fixture.json`
- `issue_agent/__init__.py`
- `issue_agent/cli.py`
- `issue_agent/config.py`
- `issue_agent/github.py`
- `issue_agent/models.py`
- `issue_agent/classifier.py`
- `issue_agent/policy.py`
- `issue_agent/state.py`
- `issue_agent/preview.py`
- `tests/test_config.py`
- `tests/test_github.py`
- `tests/test_classifier_policy.py`
- `tests/test_state_preview.py`

## Open Questions for Planning

None blocking. The plan can choose exact module names and command names within the context decisions.

## RESEARCH COMPLETE
