---
phase: 01-core-preview-pipeline
plan: "03"
subsystem: classifier-policy
tags: [python, pydantic, classifier, policy, preview-state]
requires:
  - phase: 01-02
    provides: Typed issue and label intake
provides:
  - Classifier proposal, policy decision, preview record, and batch preview schemas
  - Fixture classifier provider and provider protocol
  - Deterministic policy rejecting absent labels and unsafe output
  - Preview artifacts containing model proposal and policy result
affects:
  - 02-code-aware-triage-and-answers
  - 03-stale-cleanup-and-controlled-apply
tech-stack:
  added: []
  patterns:
    - Model output is schema-validated proposal data before policy
    - Deterministic policy owns label applyability and human-review downgrades
    - Preview state serializes Pydantic records with bounded replacement semantics
key-files:
  created:
    - issue_agent/classifier.py
    - issue_agent/policy.py
    - tests/test_classifier_policy.py
    - tests/test_state_preview.py
  modified:
    - issue_agent/models.py
    - issue_agent/cli.py
    - issue_agent/state.py
    - issue_agent/preview.py
    - tests/test_cli_skeleton.py
key-decisions:
  - "Treat classifier output as proposal data and route it through deterministic policy before state serialization."
  - "Repair invalid classifier JSON at most once, then downgrade unresolved invalid output to human_review."
  - "Keep Phase 1 preview-only and reserve CodeGraph/source-evidence fields without implementing source lookup yet."
patterns-established:
  - "Provider protocol plus deterministic fixture provider for offline tests."
  - "Policy decisions carry applyable labels, rejected labels, status, and reason."
requirements-completed:
  - CLSF-01
  - CLSF-02
  - CLSF-03
  - CLSF-04
  - SAFE-03
  - SAFE-05
  - STATE-01
  - STATE-02
  - STATE-03
duration: 4 min
completed: 2026-06-15T16:32:21Z
---

# Phase 1 Plan 03: Classifier Schema and Policy Summary

**Schema-validated classifier proposals with deterministic policy and auditable preview records**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-15T16:28:08Z
- **Completed:** 2026-06-15T16:32:21Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Added Pydantic schemas for classifier proposals, policy decisions, evidence refs, preview records, and batch previews.
- Implemented `ClassifierProvider`, deterministic `FixtureClassifierProvider`, `apply_policy`, and `parse_or_human_review`.
- Updated CLI/state/preview rendering so artifacts include `model_proposal` and `policy_decision` with bounded replacement behavior.

## Task Commits

1. **Task 1: Define classifier proposal and policy schemas** - `269627c` (feat)
2. **Task 2: Implement fixture classifier provider and policy validation** - `37b8d14` (feat)
3. **Task 3: Persist model proposal and policy result in preview artifacts** - `e7eb511` (feat)

## Files Created/Modified

- `issue_agent/models.py` - Classifier, policy, evidence, preview record, and batch preview schemas.
- `issue_agent/classifier.py` - Provider protocol, fixture classifier, and invalid-output handling.
- `issue_agent/policy.py` - Deterministic label applyability and human-review policy.
- `issue_agent/cli.py` - Preview command invoking classifier provider and policy.
- `issue_agent/state.py` - BatchPreview serialization and records replacement.
- `issue_agent/preview.py` - Markdown table with Category, Proposed, Applyable, Rejected, Status, and Reason.
- `tests/test_classifier_policy.py` - Schema, provider, policy, and repair/downgrade tests.
- `tests/test_state_preview.py` - Bounded state replacement and pending batch shape tests.
- `tests/test_cli_skeleton.py` - CLI state assertions for proposal/policy fields.

## Decisions Made

- Used a `Protocol` for `ClassifierProvider` so future MiniMax/OpenAI-compatible providers can share the same interface.
- Kept fixture classification deterministic and conservative; unmatched issues become `unknown_unsafe` / `human_review`.
- Serialized Pydantic models with `mode="json"` so future field types remain JSON-safe.

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

- `.venv/bin/python -m pytest tests/test_state_preview.py tests/test_cli_skeleton.py tests/test_classifier_policy.py` - PASSED, 10 tests.
- `.venv/bin/python -m pytest tests/test_classifier_policy.py tests/test_state_preview.py tests/test_cli_skeleton.py tests/test_github.py tests/test_config.py` - PASSED, 18 tests.
- `.venv/bin/python -m issue_agent.cli preview --config examples/config.yaml --issues-file examples/issues.fixture.json --state-root /tmp/issue-agent-preview` - PASSED, records contain `model_proposal` and `policy_decision`.
- `rg "gh issue (edit|comment|close)|create_label|delete_label" issue_agent tests` - PASSED, no matches.
- `gsd-tools query verify.key-links .planning/phases/01-core-preview-pipeline/01-03-PLAN.md` - PASSED, 3/3 links verified.

## Next Phase Readiness

Phase 1 has a complete safe preview pipeline. Phase 2 can add CodeGraph-backed source lookup and evidence-gated answer previews on top of the provider/policy/state boundaries.

## Self-Check: PASSED

---
*Phase: 01-core-preview-pipeline*
*Completed: 2026-06-15*
