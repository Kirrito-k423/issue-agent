---
phase: 02-code-aware-triage-and-answers
plan: "01"
subsystem: source-evidence
tags: [python, codegraph, source-lookup, evidence, pydantic]
requires:
  - phase: 01-03
    provides: Classifier proposal, policy decision, evidence ref, preview record, and bounded state schemas
provides:
  - CodeGraph index detection for target repositories
  - CodeGraph-first source lookup through injectable command runner
  - Fallback source search with explicit lookup mode and fallback reason
  - Source evidence fields on EvidenceRef
affects:
  - 02-code-aware-triage-and-answers
  - 03-stale-cleanup-and-controlled-apply
tech-stack:
  added: []
  patterns:
    - CodeGraph command execution is isolated behind issue_agent/codegraph.py
    - Source evidence records use repository-relative paths and explicit lookup_mode
    - Tests simulate CodeGraph through fixture directories and injected runners
key-files:
  created:
    - issue_agent/codegraph.py
    - tests/test_codegraph.py
    - tests/fixtures/source_repo/example_module.py
    - tests/fixtures/source_repo/.codegraph/.gitkeep
  modified:
    - issue_agent/models.py
key-decisions:
  - "Keep CodeGraph invocation behind an injectable adapter so tests do not require a real CodeGraph install."
  - "Use fallback_search evidence with fallback_reason to make non-CodeGraph evidence auditable."
  - "Keep minimal EvidenceRef construction backward-compatible for Phase 1 preview records."
patterns-established:
  - "CodeGraph-first lookup checks target repo .codegraph/ before fallback source search."
  - "Fallback search returns repository-relative source evidence or a source_lookup no-match record."
requirements-completed:
  - CODE-01
  - CODE-02
  - CODE-04
  - SAFE-02
duration: 7 min
completed: 2026-06-15T16:55:14Z
---

# Phase 2 Plan 01: CodeGraph Adapter and Source Evidence Summary

**CodeGraph-first source lookup with auditable fallback evidence records**

## Performance

- **Duration:** 7 min
- **Started:** 2026-06-15T16:48:00Z
- **Completed:** 2026-06-15T16:55:14Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Extended `EvidenceRef` with source lookup fields while preserving the minimal Phase 1 evidence shape.
- Added `issue_agent/codegraph.py` with `.codegraph/` detection, injectable `codegraph explore` execution, and deterministic fallback source search.
- Added offline tests and fixture source repo coverage for CodeGraph-present, CodeGraph-failure, and CodeGraph-missing behavior.

## Task Commits

1. **Task 1: Extend evidence schema for source lookup** - `4adb7d0` (feat)
2. **Task 2: Implement CodeGraph-first lookup adapter** - `2b92d5b` (feat)
3. **Task 3: Add fallback source search with explicit evidence mode** - `759bdf1` (feat)

## Files Created/Modified

- `issue_agent/models.py` - Added source lookup fields to `EvidenceRef`.
- `issue_agent/codegraph.py` - Added CodeGraph detection, command runner adapter, output parsing, and fallback search.
- `tests/test_codegraph.py` - Added schema, CodeGraph-first, fallback, and failure tests.
- `tests/fixtures/source_repo/example_module.py` - Fixture source file for lookup tests.
- `tests/fixtures/source_repo/.codegraph/.gitkeep` - Fixture marker for indexed target repo behavior.

## Decisions Made

- Used an injectable command runner rather than calling CodeGraph directly in tests.
- Represented missing or failed CodeGraph as explicit fallback evidence rather than silently hiding the lookup mode.
- Kept fallback search local and deterministic so Phase 2 remains offline-testable.

## Deviations from Plan

None - plan executed exactly as written.

---

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No scope change.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Verification

- `.venv/bin/python -m pytest tests/test_codegraph.py tests/test_classifier_policy.py tests/test_state_preview.py` - PASSED, 16 tests.
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" query verify.key-links .planning/phases/02-code-aware-triage-and-answers/02-01-PLAN.md` - PASSED, 2/2 links verified.
- `rg "gh issue (edit|comment|close)|create_label|delete_label" issue_agent tests` - PASSED, no matches.

## Next Phase Readiness

The source evidence adapter is ready for 02-02 policy gates and 02-03 answer-preview orchestration. The next plan can consume `lookup_source_evidence` and `EvidenceRef.lookup_mode` without needing live CodeGraph.

## Self-Check: PASSED

---
*Phase: 02-code-aware-triage-and-answers*
*Completed: 2026-06-15*
