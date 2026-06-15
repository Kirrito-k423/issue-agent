---
phase: 02-code-aware-triage-and-answers
plan: "02"
subsystem: answer-policy
tags: [python, policy, classifier, evidence-gates, safety]
requires:
  - phase: 02-01
    provides: Source evidence schema fields and CodeGraph/fallback lookup adapter
provides:
  - Answer policy decision model
  - Deterministic no-answer gates for unverified reproduction issues
  - Source-evidence requirement for code logic answers
  - Fixture classifier routing for code questions and reproduction issues
affects:
  - 02-code-aware-triage-and-answers
  - 03-stale-cleanup-and-controlled-apply
tech-stack:
  added: []
  patterns:
    - Reply-worthiness is evaluated before any draft generation
    - Reproduction issues require run evidence before replies
    - Code logic questions require source evidence before replies
key-files:
  created:
    - tests/test_answer_policy.py
  modified:
    - issue_agent/models.py
    - issue_agent/policy.py
    - issue_agent/classifier.py
    - examples/issues.fixture.json
    - tests/test_classifier_policy.py
key-decisions:
  - "Use AnswerPolicyDecision to keep reply-worthiness separate from draft text generation."
  - "Route unverified experiment/reproduction issues to request_info with reason requires_unverified_reproduction."
  - "Route code logic questions without source evidence to human_review with reason missing_source_evidence."
patterns-established:
  - "Answer policy consumes classifier category plus source/run evidence and fails closed."
  - "Fixture provider covers usage, bug, code-logic, and experiment-reproduction categories."
requirements-completed:
  - CODE-03
  - SAFE-01
  - SAFE-02
  - ANS-03
duration: 4 min
completed: 2026-06-15T16:58:08Z
---

# Phase 2 Plan 02: No-Answer Gates Summary

**Deterministic reply-worthiness gates for unverified reproduction and missing-source code questions**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-15T16:54:00Z
- **Completed:** 2026-06-15T16:58:08Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Added `AnswerPolicyDecision` and `evaluate_answer_policy` for preview-safe reply-worthiness decisions.
- Extended the fixture classifier and fixture issue batch to include `code_logic_question` and `experiment_reproduction` cases.
- Enforced deterministic gates for `requires_unverified_reproduction`, `missing_source_evidence`, and unknown/unsafe human review.

## Task Commits

1. **Task 1: Add answer policy decision shape** - `b986254` (feat)
2. **Task 2: Classify code questions and reproduction issues in fixtures** - `95430f5` (feat)
3. **Task 3: Enforce source-evidence and uncertainty gates** - `52b89d0` (feat)

## Files Created/Modified

- `issue_agent/models.py` - Added `AnswerPolicyDecision`.
- `issue_agent/policy.py` - Added `evaluate_answer_policy` and source/run evidence gates.
- `issue_agent/classifier.py` - Added deterministic code-logic and reproduction fixture signals.
- `examples/issues.fixture.json` - Added code question and reproduction/environment fixture issues.
- `tests/test_classifier_policy.py` - Added category assertions for new fixture issues.
- `tests/test_answer_policy.py` - Added no-answer and source-evidence policy tests.

## Decisions Made

- Kept answer policy deterministic and independent from answer text generation.
- Used explicit machine-readable skip reasons so previews can explain why drafts are absent.
- Preserved Phase 1 classifier tests by making new category signals more specific than generic usage or bug signals.

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

- `.venv/bin/python -m pytest tests/test_answer_policy.py tests/test_classifier_policy.py` - PASSED, 12 tests.
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" query verify.key-links .planning/phases/02-code-aware-triage-and-answers/02-02-PLAN.md` - PASSED, 2/2 links verified.
- `rg "gh issue (edit|comment|close)|create_label|delete_label" issue_agent tests` - PASSED, no matches.

## Next Phase Readiness

The answer-preview workflow can now consume reply-worthiness decisions and only render drafts for issues that pass source/run evidence gates.

## Self-Check: PASSED

---
*Phase: 02-code-aware-triage-and-answers*
*Completed: 2026-06-15*
