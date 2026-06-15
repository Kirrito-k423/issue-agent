---
phase: 03-stale-cleanup-and-controlled-apply
plan: "03"
subsystem: explicit-apply
tags: [python, github, apply, cli, state, safety]
requires:
  - phase: 03-stale-cleanup-and-controlled-apply
    plan: "02"
    provides: Evidence-gated close preview records and local close state
provides:
  - Explicit apply action and result models
  - Preview-record validation for apply mode
  - Narrow GitHub mutation adapter with fake-runner tests
  - Apply result state under apply/
  - Explicit `apply-close` CLI command
affects:
  - 03-stale-cleanup-and-controlled-apply
  - 04-summary-tests-and-operator-docs
tech-stack:
  added: []
  patterns:
    - Apply mode consumes reviewed preview records and does not recompute policy.
    - Public GitHub mutations are isolated to a narrow adapter.
    - Tests inject fake runners and never execute live `gh`.
key-files:
  created:
    - issue_agent/apply.py
    - tests/test_apply.py
  modified:
    - issue_agent/models.py
    - issue_agent/github.py
    - issue_agent/state.py
    - issue_agent/preview.py
    - issue_agent/cli.py
    - tests/test_cli_skeleton.py
    - README.md
key-decisions:
  - "Reject apply requests before any mutation when close preview records are missing or mismatched."
  - "Keep close preview records unchanged after apply; write separate apply result records."
  - "Do not introduce label creation, GitHub App auth, dashboards, scheduling, or summary reporting in this phase."
patterns-established:
  - "apply_close_actions(state_root, repo, actions, mutation_runner) validates all actions before execution."
  - "GitHubMutationRunner is the only implementation boundary that builds `gh issue` mutation argv."
  - "write_apply_results(state_root, results) records applied, failed, and skipped action outcomes."
requirements-completed:
  - CLOSE-03
  - APPLY-01
  - APPLY-02
  - APPLY-03
  - APPLY-04
duration: 6 min
completed: 2026-06-15T17:34:57Z
---

# Phase 3 Plan 03: Explicit Apply Summary

**Reviewed close-preview records can now be applied through an explicit, auditable mutation boundary**

## Performance

- **Duration:** 6 min
- **Started:** 2026-06-15T17:29:00Z
- **Completed:** 2026-06-15T17:34:57Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Added `ApplyAction` and `ApplyResult` models for separate label, comment, and close actions.
- Added `issue_agent/apply.py` with close-preview loading, validation, deterministic action order, failure recording, and no retry loops.
- Added `GitHubMutationRunner` as the only adapter that builds `gh issue edit/comment/close` argv.
- Added `write_apply_results` and apply Markdown rendering under `apply/`.
- Added explicit `apply-close` CLI command and README warnings that apply mode can mutate GitHub only after preview records exist.

## Task Commits

1. **Tasks 1-3: Explicit apply engine, adapter, CLI, state, and tests** - `cc43cfc` (feat)

## Files Created/Modified

- `issue_agent/models.py` - Added apply action/status/result models.
- `issue_agent/apply.py` - Added preview-record validation and apply execution engine.
- `issue_agent/github.py` - Added narrow `GitHubMutationRunner` adapter and command result shape.
- `issue_agent/preview.py` - Added apply result Markdown renderer.
- `issue_agent/state.py` - Added bounded apply result state writer.
- `issue_agent/cli.py` - Added explicit `apply-close` command.
- `tests/test_apply.py` - Added fake-runner validation, argv, failure, and state preservation tests.
- `tests/test_cli_skeleton.py` - Added CLI help assertion for explicit apply command.
- `README.md` - Documented apply command and safety boundary.

## Decisions Made

- Apply validation rejects missing preview state, missing issue records, unsuitable close previews, missing draft comments, and mismatched comment bodies before any mutation call.
- Label actions require a reviewed issue preview and an explicit label value, but no label creation command exists.
- A failed required comment skips only its dependent close action and does not trigger retries.
- `close/records.json` remains the evidence source and is preserved after apply; mutation outcomes live under `apply/`.

## Deviations from Plan

None.

## Issues Encountered

None.

## User Setup Required

Apply mode requires the GitHub CLI (`gh`) to be authenticated when the operator intentionally runs the non-test CLI against a real repository.

## Verification

- `.venv/bin/python -m pytest tests/test_apply.py tests/test_close_preview.py` - PASSED, 11 tests.
- `.venv/bin/python -m pytest tests/test_apply.py` - PASSED, 6 tests.
- `.venv/bin/python -m pytest tests/test_apply.py tests/test_close_preview.py tests/test_cli_skeleton.py tests/test_github.py tests/test_config.py` - PASSED, 21 tests.
- `.venv/bin/python -m pytest` - PASSED, 57 tests.
- `rg "evaluate_closure_policy|apply_policy|FixtureClassifierProvider" issue_agent/apply.py` - PASSED, no apply-time policy/classifier dependency.
- `rg '"gh", "issue", "(edit|comment|close)"|gh issue' issue_agent tests README.md` - PASSED, mutation strings isolated to `issue_agent/github.py`, `tests/test_apply.py`, and `README.md`.

## Next Phase Readiness

Phase 4 can now build summary reports, broaden regression coverage, and write operator docs over the full classify, answer, close-preview, and apply workflow.

## Self-Check: PASSED

---
*Phase: 03-stale-cleanup-and-controlled-apply*
*Completed: 2026-06-15*
