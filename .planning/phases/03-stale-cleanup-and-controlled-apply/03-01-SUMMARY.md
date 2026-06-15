---
phase: 03-stale-cleanup-and-controlled-apply
plan: "01"
subsystem: linked-evidence
tags: [python, github, fixtures, evidence, parsing, pydantic]
requires:
  - phase: 02-code-aware-triage-and-answers
    provides: Evidence models, fixture issue intake, and preview-safe workflow patterns
provides:
  - Linked reference model for issue and PR evidence
  - Offline parser for GitHub URLs, owner/repo#number, and #number references
  - Stale cleanup fixture cases for help-wanted/open-PR and waiting-for-info scenarios
affects:
  - 03-stale-cleanup-and-controlled-apply
  - 04-summary-tests-and-operator-docs
tech-stack:
  added: []
  patterns:
    - Linked evidence is parsed locally from issue body and comments before policy decisions.
    - Unknown linked status remains explicit and is not treated as closure evidence.
key-files:
  created:
    - issue_agent/links.py
    - tests/test_links.py
  modified:
    - issue_agent/models.py
    - examples/issues.fixture.json
    - tests/test_github.py
    - tests/test_cli_skeleton.py
key-decisions:
  - "Keep linked-reference parsing offline and fixture-testable; no live GitHub calls in the evidence extraction layer."
  - "Represent issue and PR links as typed records with relation, source, status, and reason."
  - "Preserve old-but-not-closable fixtures so closure policy can prove age alone is insufficient."
patterns-established:
  - "extract_linked_references(issue, default_repo) returns structured LinkedReference records from body and comments."
  - "Fixture expansion preserves existing issue order and appends stale cleanup cases."
requirements-completed:
  - GH-03
  - SAFE-04
  - CLOSE-02
duration: 6 min
completed: 2026-06-15T17:22:53Z
---

# Phase 3 Plan 01: Linked Evidence Extraction Summary

**Structured issue and PR reference evidence for stale cleanup decisions**

## Performance

- **Duration:** 6 min
- **Started:** 2026-06-15T17:16:45Z
- **Completed:** 2026-06-15T17:22:53Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Added `LinkedReference` and related literal types for structured linked issue/PR evidence.
- Added `issue_agent/links.py` with offline extraction for GitHub URLs, `owner/repo#number`, and `#number` references in issue bodies and comments.
- Expanded fixture issues with stale cleanup examples covering old help-wanted/open-PR work and waiting-for-info evidence.

## Task Commits

1. **Task 1: Add linked-reference schema** - `ff4618f` (feat)
2. **Task 2: Parse linked issue and PR references** - `7fa6e9f` (feat)
3. **Task 3: Extend fixtures for stale cleanup evidence** - `e59c3cc` (feat)
4. **Task 3 follow-up: Update fixture preview expectations** - `0d9eb6c` (fix)

## Files Created/Modified

- `issue_agent/models.py` - Added linked-reference kind, relation, status, and model types.
- `issue_agent/links.py` - Added body/comment linked-reference parser and conservative relation inference.
- `examples/issues.fixture.json` - Added issue 5 and issue 6 stale cleanup fixture cases.
- `tests/test_links.py` - Added schema, parser, and fixture evidence tests.
- `tests/test_github.py` - Updated fixture intake order expectations.
- `tests/test_cli_skeleton.py` - Updated classification preview expectations for expanded fixtures.

## Decisions Made

- Kept reference status defaulting to `unknown` so later closure policy cannot treat unresolved linked references as proof of closure suitability.
- Used a local parser rather than live GitHub resolution in this plan, leaving status resolution for future adapter work.
- Added waiting-for-info and help-wanted/open-PR fixtures now so 03-02 can test conservative closure policy directly.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Update classification CLI expectation after fixture expansion**
- **Found during:** Plan-level verification.
- **Issue:** `tests/test_cli_skeleton.py` still expected four fixture records after Task 3 intentionally expanded the fixture batch to six records.
- **Fix:** Updated the test to expect records `1` through `6`.
- **Files modified:** `tests/test_cli_skeleton.py`.
- **Verification:** `.venv/bin/python -m pytest tests/test_links.py tests/test_github.py tests/test_classifier_policy.py tests/test_answer_preview.py tests/test_cli_skeleton.py` passed, 26 tests.
- **Committed in:** `0d9eb6c`

---

**Total deviations:** 1 auto-fixed (1 blocking).
**Impact on plan:** Fixture expansion remains intentional and aligned with Phase 3. No scope creep.

## Issues Encountered

None beyond the auto-fixed test expectation above.

## User Setup Required

None - no external service configuration required.

## Verification

- `.venv/bin/python -m pytest tests/test_links.py tests/test_github.py` - PASSED, 12 tests.
- `.venv/bin/python -m pytest tests/test_links.py tests/test_github.py tests/test_classifier_policy.py tests/test_answer_preview.py tests/test_cli_skeleton.py` - PASSED, 26 tests.
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" query verify.key-links .planning/phases/03-stale-cleanup-and-controlled-apply/03-01-PLAN.md` - PASSED, 2/2 links verified.
- `rg "gh issue (edit|comment|close)|create_label|delete_label" issue_agent tests README.md` - PASSED, no preview mutation matches.

## Next Phase Readiness

03-02 can now consume `LinkedReference` and `extract_linked_references` to build evidence-gated closure recommendations and close-preview state.

## Self-Check: PASSED

---
*Phase: 03-stale-cleanup-and-controlled-apply*
*Completed: 2026-06-15*
